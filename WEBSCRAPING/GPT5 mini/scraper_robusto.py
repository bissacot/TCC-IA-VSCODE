"""
scraper_robusto.py

Instalação:
    pip install requests beautifulsoup4 tenacity

Uso:
    python scraper_robusto.py --workers 10 --batch-size 20 --output produtos.csv

Descrição:
    Scraper robusto e concorrente para http://books.toscrape.com/
    - Requisições com Session reutilizável, timeout e rotação de User-Agent.
    - Retry com backoff exponencial + jitter (tenacity) para conexões, timeouts e códigos HTTP 429/5xx.
    - Paginação detectada dinamicamente seguindo o botão "Next".
    - Processamento de páginas em paralelo com ThreadPoolExecutor.
    - Parsing com BeautifulSoup: título completo, preço, disponibilidade, avaliação (1-5), URL absoluta da imagem.
    - Persistência contínua em `produtos.csv` via thread escritora (thread-safe), sem acumular tudo em memória.
"""

from __future__ import annotations

import argparse
import csv
import logging
import random
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from queue import Empty, Queue
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from tenacity import (
    RetryError,
    before_sleep_log,
    retry,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_random_exponential,
)

# ---------- Configuração de logging ----------
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s"
)
logger = logging.getLogger("scraper_robusto")

# ---------- User-Agents modernos (rotacionados aleatoriamente) ----------
USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/16.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.5790.170 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Edg/120.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/16.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.5790.170 Mobile Safari/537.36",
]

# ---------- Mapeamento das classes de avaliação para inteiros ----------
RATING_MAP: Dict[str, int] = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


@dataclass
class Product:
    """Representa um produto extraído do site."""

    title: str
    price: str
    price_value: Optional[float]
    availability: str
    rating: int
    image_url: str
    product_page_url: str


class Scraper:
    """
    Scraper robusto para books.toscrape.com.

    Responsibilities:
    - Gerenciar sessão HTTP com timeout, UA rotativo e adapter de conexões.
    - Descobrir páginas dinamicamente seguindo o botão 'Next'.
    - Processar páginas em paralelo e enviar produtos para a fila de escrita.
    - Gerenciar thread escritora que persiste dados em CSV em lotes.
    """

    RETRY_STATUS_CODES = {429, 500, 502, 503, 504}

    def __init__(
        self,
        base_url: str = "http://books.toscrape.com/",
        workers: int = 5,
        output_file: str = "produtos.csv",
        batch_size: int = 20,
        max_retries: int = 5,
    ) -> None:
        """
        Args:
            base_url: URL inicial do site.
            workers: Número de threads concorrentes para processar páginas.
            output_file: Caminho do CSV de saída.
            batch_size: Quantos registros agrupar antes de gravar no CSV.
            max_retries: Tentativas máximas por requisição antes de falhar.
        """
        self.base_url = base_url
        self.workers = max(1, int(workers))
        self.output_file = output_file
        self.batch_size = max(1, int(batch_size))
        self.max_retries = max(1, int(max_retries))

        self.session: Optional[requests.Session] = None
        self._queue: "Queue[List[Any]]" = Queue()
        self._writer_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._csv_header = [
            "title",
            "price",
            "price_value",
            "availability",
            "rating",
            "image_url",
            "product_page_url",
        ]

    def _random_user_agent(self) -> str:
        """Retorna um User-Agent aleatório."""
        return random.choice(USER_AGENTS)

    def _build_session(self) -> requests.Session:
        """
        Cria e configura uma requests.Session com HTTPAdapter para pool de conexões.

        Returns:
            requests.Session: sessão configurada.
        """
        session = requests.Session()
        # Ajuste de pool para concorrência
        pool_size = max(10, self.workers * 4)
        adapter = HTTPAdapter(pool_connections=pool_size, pool_maxsize=pool_size)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _request(
        self, method: str, url: str, **kwargs: Any
    ) -> requests.Response:
        """
        Realiza uma requisição HTTP com retry (exponencial + jitter) usando tenacity.

        Re-tries aplicam a:
         - RequestException (conexão, DNS, timeout, etc.)
         - Respostas com status em RETRY_STATUS_CODES

        Args:
            method: 'GET', 'POST', etc.
            url: URL alvo.
            **kwargs: Passados para session.request (timeout será padrão 10s).

        Returns:
            requests.Response: resposta final.
        Raises:
            RequestException / RetryError: em falhas irreversíveis.
        """
        if self.session is None:
            raise RuntimeError("Session HTTP não inicializada")

        # Função real que fará a requisição (decorada dinamicamente para permitir max_retries configurável)
        def _do_request(method_: str, url_: str, **kwargs_: Any) -> requests.Response:
            headers = kwargs_.pop("headers", {}) or {}
            headers["User-Agent"] = self._random_user_agent()
            timeout_value = kwargs_.pop("timeout", 10)
            try:
                resp = self.session.request(
                    method_, url_, headers=headers, timeout=timeout_value, **kwargs_
                )
                return resp
            except RequestException:
                # Re-raise para que tenacity capture e execute retry
                raise

        # Condição para retry baseada no resultado (status HTTP)
        def _should_retry_result(resp: Optional[requests.Response]) -> bool:
            return resp is not None and resp.status_code in self.RETRY_STATUS_CODES

        # Cria o decorator dinamicamente para usar self.max_retries e registrar tentativas
        decorated = retry(
            reraise=True,
            stop=stop_after_attempt(self.max_retries),
            wait=wait_random_exponential(multiplier=1, max=60),
            retry=(
                retry_if_exception_type(RequestException)
                | retry_if_result(_should_retry_result)
            ),
            before_sleep=before_sleep_log(logger, logging.WARNING),
        )(_do_request)

        try:
            response = decorated(method, url, **kwargs)
        except RetryError as re:
            # Extrai a última exceção ou resultado para log mais útil
            last_attempt = re.last_attempt
            logger.error("Falha após retries em %s: %s", url, re)
            raise
        return response

    def _discover_all_pages(self) -> List[str]:
        """
        Descobre todas as URLs de paginação seguindo o botão 'Next'.

        Returns:
            Lista de URLs completas de todas as páginas encontradas.
        """
        pages: List[str] = []
        current_url = self.base_url
        logger.info("Iniciando descoberta de páginas a partir de %s", self.base_url)

        while True:
            try:
                resp = self._request("GET", current_url)
            except Exception as exc:
                logger.exception("Erro ao buscar página %s: %s", current_url, exc)
                raise

            pages.append(current_url)
            soup = BeautifulSoup(resp.text, "html.parser")
            next_link = soup.select_one("li.next > a")
            if not next_link:
                break
            href = next_link.get("href")
            if not href:
                break
            # Resolve URL relativa
            current_url = urljoin(current_url, href)

        logger.info("Descobertas %d páginas", len(pages))
        return pages

    def _process_page(self, page_url: str) -> int:
        """
        Processa uma página de listagem: extrai produtos e envia para a fila de escrita.

        Args:
            page_url: URL completa da página.
        Returns:
            Número de produtos extraídos.
        """
        try:
            resp = self._request("GET", page_url)
        except Exception:
            logger.exception("Falha ao recuperar página %s", page_url)
            return 0

        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select("article.product_pod")
        count = 0

        for item in items:
            # Título completo (atributo title do <a> dentro de h3)
            a_tag = item.find("h3").find("a")
            title = a_tag.get("title", "").strip()

            # Preço
            price_tag = item.select_one("p.price_color")
            price_text = price_tag.text.strip() if price_tag else ""

            # Extrair valor numérico do preço (ex: '£51.77' -> 51.77)
            price_value: Optional[float] = None
            m = re.search(r"[\d\.,]+", price_text)
            if m:
                try:
                    price_value = float(m.group().replace(",", ""))
                except ValueError:
                    price_value = None

            # Disponibilidade
            availability_tag = item.select_one("p.instock.availability")
            availability = (
                availability_tag.get_text(strip=True) if availability_tag else ""
            )

            # Avaliação em estrelas (classe do p.star-rating)
            rating_tag = item.select_one("p.star-rating")
            rating = 0
            if rating_tag and rating_tag.has_attr("class"):
                for cls in rating_tag["class"]:
                    if cls in RATING_MAP:
                        rating = RATING_MAP[cls]
                        break

            # URL absoluta da imagem
            img_tag = item.select_one("div.image_container img")
            img_src = img_tag.get("src") if img_tag else ""
            image_url = urljoin(page_url, img_src)

            # URL da página do produto (relativa -> absoluta)
            href = a_tag.get("href", "")
            product_url = urljoin(page_url, href)

            product = Product(
                title=title,
                price=price_text,
                price_value=price_value,
                availability=availability,
                rating=rating,
                image_url=image_url,
                product_page_url=product_url,
            )

            # Enfileira como lista pronta para CSV (sem acumular em memória global)
            row: List[Any] = [
                product.title,
                product.price,
                product.price_value if product.price_value is not None else "",
                product.availability,
                product.rating,
                product.image_url,
                product.product_page_url,
            ]
            self._queue.put(row)
            count += 1

        logger.info("Página %s: extraídos %d produtos", page_url, count)
        return count

    def _writer_worker(self, csvfile, stop_event: threading.Event) -> None:
        """
        Worker que consome a fila e grava no CSV em lotes.

        Args:
            csvfile: arquivo CSV já aberto (modo append) pelo contexto chamador.
            stop_event: evento que sinaliza término quando todas as páginas foram processadas.
        """
        writer = csv.writer(csvfile)
        buffer: List[List[Any]] = []

        # Escreve cabeçalho já deverá ter sido escrito pelo chamador ao abrir o arquivo.
        while not stop_event.is_set() or not self._queue.empty():
            try:
                row = self._queue.get(timeout=1.0)
                buffer.append(row)
                self._queue.task_done()
            except Empty:
                # Caso não haja itens, grava buffer pendente se existir
                if buffer:
                    writer.writerows(buffer)
                    csvfile.flush()
                    buffer.clear()
                continue

            if len(buffer) >= self.batch_size:
                writer.writerows(buffer)
                csvfile.flush()
                buffer.clear()

        # Ao finalizar, grava qualquer buffer restante
        if buffer:
            writer.writerows(buffer)
            csvfile.flush()
            buffer.clear()

        logger.info("Writer finalizado, arquivo salvo em %s", self.output_file)

    def run(self) -> None:
        """
        Execução principal do scraper:
        - Inicia sessão HTTP e writer thread.
        - Descobre páginas e processa em paralelo.
        - Aguarda finalização e finaliza recursos.
        """
        logger.info(
            "Iniciando scraper: base=%s workers=%d output=%s",
            self.base_url,
            self.workers,
            self.output_file,
        )

        # Inicializa sessão e arquivo CSV (context managers garantem fechamento)
        with self._build_session() as session:
            self.session = session

            # Header do CSV: abrimos em 'w' para sobrescrever e escrever cabeçalho
            with open(self.output_file, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(self._csv_header)
                csvfile.flush()

                # Inicia thread escritora (ela consumirá a mesma file handle)
                self._stop_event.clear()
                self._writer_thread = threading.Thread(
                    target=self._writer_worker, args=(csvfile, self._stop_event), daemon=True
                )
                self._writer_thread.start()

                # Descobre páginas (sequencial, pois depende do Next)
                try:
                    page_urls = self._discover_all_pages()
                except Exception:
                    # Em caso de erro na descoberta, sinaliza parar e re-raise
                    self._stop_event.set()
                    self._writer_thread.join()
                    raise

                # Processa páginas em paralelo
                with ThreadPoolExecutor(max_workers=self.workers) as executor:
                    futures = {executor.submit(self._process_page, url): url for url in page_urls}
                    for future in as_completed(futures):
                        page = futures[future]
                        try:
                            future.result()
                        except Exception:
                            logger.exception("Erro processando página %s", page)

                # Aguarda fila esvaziar e encerra writer
                # Dá um pequeno tempo para consumidores terminarem de enfileirar
                logger.info("Todas as páginas processadas; aguardando fila de escrita...")
                # Espera até que a fila esteja vazia
                while not self._queue.empty():
                    time.sleep(0.5)

                # Sinaliza término para writer e aguarda join
                self._stop_event.set()
                if self._writer_thread:
                    self._writer_thread.join(timeout=30)

        logger.info("Scraping concluído. Arquivo: %s", self.output_file)


def build_arg_parser() -> argparse.ArgumentParser:
    """Constrói o parser de argumentos de linha de comando."""
    parser = argparse.ArgumentParser(description="Scraper robusto para books.toscrape.com")
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Número de workers (threads) para processar páginas em paralelo.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="Tamanho do lote de escrita no CSV (quantos registros por escrita).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="produtos.csv",
        help="Caminho do arquivo CSV de saída.",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://books.toscrape.com/",
        help="URL base para iniciar o scraping (padrão: http://books.toscrape.com/).",
    )
    return parser


def main() -> None:
    """Ponto de entrada quando executado como script."""
    parser = build_arg_parser()
    args = parser.parse_args()
    scraper = Scraper(
        base_url=args.base_url,
        workers=args.workers,
        output_file=args.output,
        batch_size=args.batch_size,
    )
    try:
        scraper.run()
    except KeyboardInterrupt:
        logger.warning("Interrompido pelo usuário (KeyboardInterrupt). Encerrando.")
    except Exception:
        logger.exception("Ocorreu um erro durante a execução do scraper.")


if __name__ == "__main__":
    main()