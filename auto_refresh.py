import os
import time
import random
import uuid
from datetime import datetime, timedelta
import psycopg2
from dotenv import load_dotenv

load_dotenv()

class WorkingDataGenerator:
    def __init__(self):
        # Add connection debug info
        print("🔍 Testing database connection...")
        print(f"Host: {os.getenv('DB_HOST', 'Not set')}")
        print(f"Database: {os.getenv('DB_NAME', 'Not set')}")
        print(f"User: {os.getenv('DB_USER', 'Not set')}")
        
        # Connect to Superset database - using Docker container names
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "superset"),  # Default to superset
            user=os.getenv("DB_USER", "superset"),    # Default to superset user
            password=os.getenv("DB_PASSWORD", "superset"),  # Default to superset password
            host=os.getenv("DB_HOST", "db"),          # Default to 'db' container name
            port=os.getenv("DB_PORT", "5432")         # Default PostgreSQL port
        )
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()
        
        # Test the connection
        self.test_connection()
        
        self.customer_ids = []
        self.seller_ids = []
        self.product_ids = []
        self.load_valid_ids()

    def test_connection(self):
        """Test database connection and show current database info"""
        try:
            self.cursor.execute("SELECT current_database(), current_user, version();")
            db_info = self.cursor.fetchone()
            print(f"✅ Connected to database: {db_info[0]}")
            print(f"✅ User: {db_info[1]}")
            print(f"✅ PostgreSQL: {db_info[2].split(',')[0]}")
            
            # Check if our tables exist
            self.cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'olist_%'
            """)
            tables = [row[0] for row in self.cursor.fetchall()]
            print(f"✅ Found tables: {tables}")
            
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            raise

    def load_valid_ids(self):
        """Load valid IDs with CORRECT column names"""
        try:
            # Get customers - CORRECT columns
            self.cursor.execute("SELECT customer_id, customer_city, customer_state FROM olist_customers LIMIT 100")
            self.customer_ids = [row for row in self.cursor.fetchall()]
            
            # Get sellers - CORRECT: using sellercity instead of seller_city
            self.cursor.execute("SELECT sellerid, sellercity, sellerstate FROM olist_sellers LIMIT 50")
            self.seller_ids = [row for row in self.cursor.fetchall()]
            
            # Get product IDs
            self.cursor.execute("SELECT product_id FROM olist_products LIMIT 100")
            self.product_ids = [row[0] for row in self.cursor.fetchall()]
            
            print(f"✅ Loaded {len(self.customer_ids)} customers, {len(self.seller_ids)} sellers, {len(self.product_ids)} products")
            
        except Exception as e:
            print(f"❌ Error loading valid IDs: {e}")
            print("💡 Make sure your tables exist in the Superset database.")
            print("   You may need to run your table creation scripts first.")

    def generate_order_id(self):
        """Generate a unique order ID since it's not auto-incrementing"""
        return str(uuid.uuid4())[:32]  # Match the format of existing order_ids

    def generate_customer_id(self):
        """Generate a valid customer ID"""
        return random.choice(self.customer_ids)[0] if self.customer_ids else "test_customer_123"

    def generate_august_2018_date(self):
        """Generate random date between Aug 14-24, 2018"""
        start_date = datetime(2018, 8, 14)
        end_date = datetime(2018, 8, 24)
        days_between = (end_date - start_date).days
        random_days = random.randint(0, days_between)
        return start_date + timedelta(days=random_days)

    def insert_complete_order(self):
        """Insert a complete order with all required fields"""
        try:
            if not self.customer_ids or not self.seller_ids or not self.product_ids:
                print("Missing required data")
                return None, 0, None, None
            
            # Generate all required IDs
            order_id = self.generate_order_id()
            customer_id = self.generate_customer_id()
            seller_id = random.choice(self.seller_ids)[0]
            product_id = random.choice(self.product_ids)
            
            # Generate order dates BETWEEN Aug 14-24, 2018 ONLY
            order_date = self.generate_august_2018_date()
            estimated_delivery = order_date + timedelta(days=random.randint(5, 15))
            
            # Order status
            status_options = ['delivered', 'shipped', 'processing', 'approved']
            status = random.choice(status_options)
            
            # Generate timestamps based on status
            approved_at = order_date + timedelta(hours=random.randint(1, 24)) if status in ['approved', 'processing', 'shipped', 'delivered'] else None
            delivered_carrier = order_date + timedelta(days=random.randint(1, 3)) if status in ['shipped', 'delivered'] else None
            delivered_customer = order_date + timedelta(days=random.randint(5, 12)) if status == 'delivered' else None
            
            # Insert into olist_orders - PROVIDING order_id explicitly
            self.cursor.execute("""
                INSERT INTO olist_orders (
                    order_id, customer_id, order_status, order_purchase_timestamp,
                    order_approved_at, order_delivered_carrier_date,
                    order_delivered_customer_date, order_estimated_delivery_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                order_id,  # Explicitly providing order_id
                customer_id,
                status,
                order_date,
                approved_at,
                delivered_carrier,
                delivered_customer,
                estimated_delivery
            ))
            
            # Insert order items
            price = round(random.uniform(25.0, 350.0), 2)
            freight_value = round(random.uniform(8.0, 35.0), 2)
            
            self.cursor.execute("""
                INSERT INTO olist_order_items (
                    order_id, order_item_id, product_id, seller_id,
                    shipping_limit_date, price, freight_value
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                order_id, 1, product_id, seller_id,
                order_date + timedelta(days=3),
                price, freight_value
            ))
            
            # Insert payment
            payment_value = round(price + freight_value, 2)
            payment_types = ['credit_card', 'boleto', 'voucher', 'debit_card']
            payment_type = random.choices(payment_types, weights=[0.7, 0.15, 0.1, 0.05])[0]
            
            self.cursor.execute("""
                INSERT INTO olist_order_payments (
                    order_id, payment_sequential, payment_type,
                    payment_installments, payment_value
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                order_id, 1, payment_type,
                random.randint(1, 6), payment_value
            ))
            
            print(f"✅ Successfully inserted order {order_id} on {order_date.date()}")
            return order_id, payment_value, status, order_date
            
        except Exception as e:
            print(f"❌ Error inserting order: {e}")
            return None, 0, None, None

    def run_auto_refresh(self, interval=15):
        """Main loop to insert orders"""
        print("🔄 Starting Olist E-commerce Data Auto-Refresh (Aug 14-24, 2018)...")
        print("Press Ctrl+C to stop the script\n")
        
        order_count = 0
        
        try:
            while True:
                order_id, amount, status, order_date = self.insert_complete_order()
                
                if order_id:
                    order_count += 1
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Order #{order_count} (Date: {order_date.date()}) - "
                          f"Amount: R${amount:.2f} - Status: {status}")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Failed to insert order")
                    # Try to reload IDs
                    time.sleep(5)
                    self.load_valid_ids()
                
                print(f"⏳ Waiting {interval} seconds...\n")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Script stopped. Total orders inserted: {order_count}")
        finally:
            self.cursor.close()
            self.conn.close()

def main():
    generator = WorkingDataGenerator()
    generator.run_auto_refresh(interval=15)

if __name__ == "__main__":
    main()