"""Main entry point for ETL pipeline."""

import argparse
import sys
from pathlib import Path
from src.etl_pipeline import ETLPipeline
from src.utils.config import load_config_from_env, load_config_from_file
from src.utils.logger import setup_logger


def main():
    """Main function to run the ETL pipeline."""
    parser = argparse.ArgumentParser(description="Sales ETL Pipeline")
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration JSON file'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Configuration file not found: {args.config}")
            sys.exit(1)
        config = load_config_from_file(args.config)
    else:
        config = load_config_from_env()
    
    # Setup logging
    logger = setup_logger(
        __name__,
        log_file="logs/etl_main.log",
        level=getattr(__import__('logging'), config.log_level)
    )
    
    # Run ETL pipeline
    try:
        pipeline = ETLPipeline(config)
        summary = pipeline.run()
        logger.info("ETL pipeline completed successfully")
        sys.exit(0)
    except Exception as e:
        logger.error(f"ETL pipeline failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
