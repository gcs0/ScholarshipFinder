import csv
import os
import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from scholarships.models import Scholarship

# Configure logging with UTF-8 encoding
class UTF8FileHandler(logging.FileHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        encoding = encoding or 'utf-8'
        super().__init__(filename, mode, encoding, delay)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        UTF8FileHandler('csv_import.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import scholarships from CSV file with error handling and logging'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            default='Scholarships.csv',
            help='Path to CSV file (default: Scholarships.csv)'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing records'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        overwrite = options['overwrite']
        
        if not os.path.exists(csv_file):
            logger.error(f"CSV file not found: {csv_file}")
            return

        logger.info(f"Starting CSV import from {csv_file}")
        logger.info(f"Overwrite mode: {overwrite}")
        
        # Clean up old logs (older than 1 week)
        self.clean_old_logs()
        
        # Import statistics
        stats = {
            'total_rows': 0,
            'successful': 0,
            'skipped': 0,
            'errors': 0,
            'updated': 0,
            'created': 0
        }
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                rows = list(csv_reader)
                
                # Find header row (row 4, index 3)
                if len(rows) < 5:
                    logger.error("CSV file too short, missing header row")
                    return
                
                header_row = rows[3]
                logger.info(f"Found header row: {len(header_row)} columns")
                
                # Process data rows (starting from row 5, index 4)
                for row_num in range(4, len(rows)):
                    row = rows[row_num]
                    stats['total_rows'] += 1
                    
                    try:
                        # Skip empty rows
                        if not row or all(not cell.strip() for cell in row):
                            stats['skipped'] += 1
                            continue
                        
                        # Parse the row
                        scholarship_data = self.parse_row(row, row_num + 1)
                        
                        if not scholarship_data:
                            stats['skipped'] += 1
                            continue
                        
                        # Save or update scholarship
                        with transaction.atomic():
                            obj, created = Scholarship.objects.update_or_create(
                                foundation_name=scholarship_data['foundation_name'],
                                scholarship_name=scholarship_data['scholarship_name'],
                                defaults=scholarship_data
                            )
                            
                            if created:
                                stats['created'] += 1
                                safe_name = scholarship_data['scholarship_name'][:50].replace('\n', ' ')
                                logger.info(f"Created: {safe_name}")
                            else:
                                stats['updated'] += 1
                                safe_name = scholarship_data['scholarship_name'][:50].replace('\n', ' ')
                                logger.info(f"Updated: {safe_name}")
                            
                            stats['successful'] += 1
                            
                    except Exception as e:
                        stats['errors'] += 1
                        logger.error(f"Error processing row {row_num + 1}: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Fatal error reading CSV: {str(e)}")
            return
        
        # Log summary
        logger.info("=" * 50)
        logger.info("CSV Import Summary:")
        logger.info(f"Total rows processed: {stats['total_rows']}")
        logger.info(f"Successfully imported: {stats['successful']}")
        logger.info(f"Created: {stats['created']}")
        logger.info(f"Updated: {stats['updated']}")
        logger.info(f"Skipped: {stats['skipped']}")
        logger.info(f"Errors: {stats['errors']}")
        logger.info("=" * 50)
        
        self.stdout.write(self.style.SUCCESS(f"Import completed: {stats['successful']} successful, {stats['errors']} errors"))

    def parse_row(self, row, row_num):
        """Parse a CSV row into scholarship data"""
        try:
            # Extract section (first column)
            section = row[0].strip() if len(row) > 0 else ""
            
            # Map section to simplified codes
            section_mapping = {
                'III. Local Govts & Intl Associations': 'III',
                'IV. Private Foundations': 'IV',
                'V. For Applicants Residing Abroad': 'V'
            }
            section_code = section_mapping.get(section, '')
            
            # Extract foundation name (column 3, index 2)
            foundation_name = row[2].strip() if len(row) > 2 else ""
            
            # Extract scholarship name (column 4, index 3)
            scholarship_name = row[3].strip() if len(row) > 3 else ""
            
            # Skip if missing required fields
            if not foundation_name or not scholarship_name:
                return None
            
            # Handle multi-line address field (column 5, index 4)
            # This field can span multiple rows, so we need to be careful
            address_contact = row[4].strip() if len(row) > 4 else ""
            
            # Extract other fields
            inquiry = row[5].strip() if len(row) > 5 else ""
            application = row[6].strip() if len(row) > 6 else ""
            qualifier = row[7].strip() if len(row) > 7 else ""
            
            # Extract remaining fields
            # CSV columns: 8=AgeLimit(skip), 9=DesignatedCountries(skip), 
            # 10=DesignatedSchools, 11=DesignatedFields, 12=PluralGrants,
            # 13=NonStudentVisa(skip), 14=AdditionalReq, 15=Contents/Award,
            # 16=Duration, 17=AppPeriod, 18=SelectionMethod, 19=Grantees, 20=PrevYear
            designated_schools = row[10].strip() if len(row) > 10 else ""
            designated_fields = row[11].strip() if len(row) > 11 else ""
            plural_grants = row[12].strip() if len(row) > 12 else ""
            additional_requirements = row[14].strip() if len(row) > 14 else ""
            contents = row[15].strip() if len(row) > 15 else ""
            duration = row[16].strip() if len(row) > 16 else ""
            application_period = row[17].strip() if len(row) > 17 else ""
            selection_method = row[18].strip() if len(row) > 18 else ""
            grantees = row[19].strip() if len(row) > 19 else ""
            grantees_applications = row[20].strip() if len(row) > 20 else ""
            
            return {
                'section': section_code,
                'foundation_name': foundation_name,
                'scholarship_name': scholarship_name,
                'address_contact': address_contact,
                'inquiry': inquiry,
                'application': application,
                'qualifier': qualifier,
                'designated_schools': designated_schools,
                'designated_fields': designated_fields,
                'plural_grants': plural_grants,
                'additional_requirements': additional_requirements,
                'contents': contents,
                'duration': duration,
                'application_period': application_period,
                'selection_method': selection_method,
                'grantees': grantees,
                'grantees_applications': grantees_applications
            }
            
        except Exception as e:
            logger.error(f"Error parsing row {row_num}: {str(e)}")
            return None

    def clean_old_logs(self):
        """Remove log files older than 1 week"""
        try:
            log_file = 'csv_import.log'
            if os.path.exists(log_file):
                file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                if timezone.now() - file_time.replace(tzinfo=timezone.utc) > timedelta(weeks=1):
                    os.remove(log_file)
                    logger.info("Removed old log file")
        except Exception as e:
            logger.warning(f"Could not clean old logs: {str(e)}")