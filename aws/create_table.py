#!/usr/bin/env python3
"""
Create DynamoDB table for Expertise Inflation Index (EII).
Run this script to set up the AWS infrastructure.
"""

import boto3
import json
import os
import sys
from botocore.exceptions import ClientError
from dotenv import load_dotenv

def create_dynamodb_table():
    """Create the EII DynamoDB table with proper schema."""
    
    # Load environment variables from .env file
    # Look for .env in parent directory if running from aws/ folder
    env_path = '../.env' if os.path.basename(os.getcwd()) == 'aws' else '.env'
    load_dotenv(env_path)
    
    # Initialize DynamoDB client
    try:
        dynamodb = boto3.client('dynamodb', 
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
    except Exception as e:
        print(f"❌ Failed to connect to AWS: {e}")
        print("Make sure your AWS credentials are configured:")
        print("  aws configure")
        print("  Or set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        return False
    
    # Load table schema
    schema_path = 'dynamodb_schema.json' if os.path.basename(os.getcwd()) == 'aws' else 'aws/dynamodb_schema.json'
    with open(schema_path, 'r') as f:
        table_config = json.load(f)
    
    table_name = table_config['TableName']
    
    try:
        # Check if table already exists
        existing_tables = dynamodb.list_tables()['TableNames']
        if table_name in existing_tables:
            print(f"✅ Table '{table_name}' already exists")
            
            # Get table details
            response = dynamodb.describe_table(TableName=table_name)
            table_status = response['Table']['TableStatus']
            table_arn = response['Table']['TableArn']
            
            print(f"📊 Status: {table_status}")
            print(f"🔗 ARN: {table_arn}")
            return True
        
        # Create the table
        print(f"🔨 Creating DynamoDB table: {table_name}")
        response = dynamodb.create_table(**table_config)
        
        print("⏳ Waiting for table to become active...")
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        
        # Get final table details
        response = dynamodb.describe_table(TableName=table_name)
        table_arn = response['Table']['TableArn']
        
        print(f"✅ Table created successfully!")
        print(f"🔗 ARN: {table_arn}")
        print(f"📊 Status: {response['Table']['TableStatus']}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceInUseException':
            print(f"✅ Table '{table_name}' already exists")
            return True
        else:
            print(f"❌ Failed to create table: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_table_access():
    """Test basic read/write access to the table."""
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        table = dynamodb.Table('eii-articles')
        
        # Test item
        test_item = {
            'article_id': 'test-article-123',
            'title': 'Test Article',
            'source': 'test.com',
            'url': 'https://test.com/article',
            'author': 'Test Author',
            'content': 'This is a test article content.',
            'published_at': '2025-01-01T00:00:00Z',
            'scored_at': '2025-01-01T00:00:00Z',
            'scores': {
                'confidence': 5,
                'jargon_density': 3,
                'self_reference': 2,
                'originality': 4,
                'humor_rating': 7,
                'overall_eii_score': 3.5,
                'analysis': {
                    'tone_summary': 'Test article with balanced tone.',
                    'inflation_type': 'Balanced',
                    'key_phrases': ['test phrase', 'example'],
                    'model_used': 'test'
                }
            }
        }
        
        # Put test item
        print("🧪 Testing write access...")
        table.put_item(Item=test_item)
        
        # Get test item
        print("🧪 Testing read access...")
        response = table.get_item(Key={'article_id': 'test-article-123'})
        
        if 'Item' in response:
            print("✅ Read/write test successful!")
            
            # Clean up test item
            table.delete_item(Key={'article_id': 'test-article-123'})
            print("🧹 Test item cleaned up")
            return True
        else:
            print("❌ Failed to read test item")
            return False
            
    except Exception as e:
        print(f"❌ Table access test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 EII DynamoDB Setup")
    print("=" * 40)
    
    # Check AWS credentials
    if not os.getenv('AWS_ACCESS_KEY_ID') and not os.getenv('AWS_PROFILE'):
        print("⚠️  AWS credentials not found in environment variables.")
        print("Make sure to run 'aws configure' or set:")
        print("  - AWS_ACCESS_KEY_ID")
        print("  - AWS_SECRET_ACCESS_KEY") 
        print("  - AWS_REGION (optional, defaults to us-east-1)")
        print()
    
    # Create table
    if create_dynamodb_table():
        print("\n🧪 Testing table access...")
        if test_table_access():
            print("\n🎉 DynamoDB setup complete!")
            print("\nNext steps:")
            print("1. Note your table ARN for n8n configuration")
            print("2. Update your .env file with AWS credentials")
            print("3. Deploy the n8n workflow")
        else:
            print("\n⚠️  Table created but access test failed")
            print("Check your AWS permissions")
    else:
        print("\n❌ Setup failed")
        print("Check your AWS credentials and permissions")

if __name__ == "__main__":
    main() 