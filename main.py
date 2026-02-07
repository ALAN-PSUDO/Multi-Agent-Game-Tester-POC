#!/usr/bin/env python3
"""
Main entry point for the Multi-Agent Game Testing System.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestrator import GameTesterOrchestrator
from src.utils.reporting import ReportGenerator
from loguru import logger


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Multi-Agent Game Testing System - Production-grade POC for automated game testing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test a single game
  python main.py --url "https://example.com/game"
  
  # Test a game with custom config
  python main.py --url "https://example.com/game" --config custom_config.yaml
  
  # Test multiple games
  python main.py --url "https://game1.com" "https://game2.com" "https://game3.com"
  
  # Generate HTML report
  python main.py --url "https://example.com/game" --report-format html
        """
    )
    
    parser.add_argument(
        '--url',
        nargs='+',
        required=True,
        help='URL(s) of the game(s) to test'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--report-format',
        choices=['json', 'text', 'html', 'all'],
        default='all',
        help='Report format (default: all)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='reports',
        help='Output directory for reports (default: reports)'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode'
    )
    
    args = parser.parse_args()
    
    # Display banner
    print("=" * 80)
    print("Multi-Agent Game Testing System v1.0.0")
    print("Production-grade POC for Automated Game Testing")
    print("Optimized for 32-bit Windows environments")
    print("=" * 80)
    print()
    
    try:
        # Initialize orchestrator
        logger.info("Initializing orchestrator...")
        orchestrator = GameTesterOrchestrator(args.config)
        
        # Override headless setting if specified
        if args.headless:
            orchestrator.config['browser']['headless'] = True
            
        # Initialize report generator
        report_generator = ReportGenerator(args.output_dir)
        
        # Test game(s)
        game_urls = args.url
        
        if len(game_urls) == 1:
            # Single game test
            logger.info(f"Testing game: {game_urls[0]}")
            result = orchestrator.test_game(game_urls[0])
            results = [result]
        else:
            # Batch test
            logger.info(f"Testing {len(game_urls)} games...")
            results = orchestrator.batch_test(game_urls)
            
        # Generate reports
        for i, result in enumerate(results):
            game_url = result.get('game_url', f'game_{i+1}')
            
            if result.get('success'):
                logger.info(f"Test completed for: {game_url}")
                logger.info(f"  Success Rate: {result.get('summary', {}).get('overall_success_rate', 0):.1%}")
                logger.info(f"  Health Score: {result.get('summary', {}).get('health_score', 0):.1f}/100")
                
                # Generate reports in requested format(s)
                if args.report_format in ['json', 'all']:
                    json_file = report_generator.generate_json_report(result)
                    print(f"  JSON Report: {json_file}")
                    
                if args.report_format in ['text', 'all']:
                    text_file = report_generator.generate_text_report(result)
                    print(f"  Text Report: {text_file}")
                    
                if args.report_format in ['html', 'all']:
                    html_file = report_generator.generate_html_report(result)
                    print(f"  HTML Report: {html_file}")
            else:
                logger.error(f"Test failed for: {game_url}")
                logger.error(f"  Error: {result.get('error', 'Unknown error')}")
                
            print()
            
        # Summary
        print("=" * 80)
        print("TESTING COMPLETE")
        print("=" * 80)
        successful_tests = sum(1 for r in results if r.get('success'))
        print(f"Total Games Tested: {len(results)}")
        print(f"Successful Tests: {successful_tests}")
        print(f"Failed Tests: {len(results) - successful_tests}")
        
        if results:
            avg_success_rate = sum(r.get('summary', {}).get('overall_success_rate', 0) for r in results if r.get('success')) / max(successful_tests, 1)
            avg_health_score = sum(r.get('summary', {}).get('health_score', 0) for r in results if r.get('success')) / max(successful_tests, 1)
            print(f"Average Success Rate: {avg_success_rate:.1%}")
            print(f"Average Health Score: {avg_health_score:.1f}/100")
        
        print()
        print(f"Reports saved to: {args.output_dir}/")
        print("=" * 80)
        
        # Return appropriate exit code
        sys.exit(0 if successful_tests == len(results) else 1)
        
    except KeyboardInterrupt:
        logger.warning("Testing interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
