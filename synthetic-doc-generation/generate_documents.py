"""
Synthetic Document Generation using ydata-sdk

This script generates synthetic invoices and bank statements for the AI agent workshop.
It uses the ydata-sdk DocumentGenerator to create realistic documents in PDF format.

Prerequisites:
- Set YDATA_LICENSE_KEY environment variable
- Install ydata-sdk: pip install ydata-sdk

Usage:
    python generate_documents.py
"""

import os
import sys
from pathlib import Path
from typing import List

# Import ydata-sdk components
from ydata.synthesizers.text.model.document import DocumentGenerator, DocumentFormat

os.environ['YDATA_LICENSE_KEY'] = '7838e01e-b652-42a9-b44f-16f507f3220f'

# Configuration
OUTPUT_DIR = Path("synthetic_pdfs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Check for license key
def check_license():
    """Ensure YDATA_LICENSE_KEY is set"""
    license_key = os.getenv('YDATA_LICENSE_KEY')
    if not license_key:
        print("Error: YDATA_LICENSE_KEY environment variable not set.")
        print("Please set your ydata-sdk license key:")
        print("export YDATA_LICENSE_KEY='your-license-key-here'")
        sys.exit(1)
    return license_key

def generate_invoices(generator: DocumentGenerator, n_docs: int = 5) -> List[str]:
    """Generate synthetic invoices"""
    print(f"\n=== Generating {n_docs} Corporate Invoices ===")
    
    generator.generate(
        n_docs=n_docs,
        document_type="Invoice",
        audience="Corporate client",
        tone="professional",
        purpose="Issue detailed invoices for consulting services rendered. Include specific line items, hourly rates, tax breakdown, and payment terms.",
        region="North America",
        language="English",
        length="Long",
        topics="Consulting services, Hourly rates, Tax breakdown, Payment terms, Line items, Subtotal, Total amount, Due date, Payment methods",
        style_guide="Professional design for a financial institution with clear formatting and detailed breakdown",
        output_dir=str(OUTPUT_DIR),
    )
    
    return list(OUTPUT_DIR.glob("*.pdf"))

def generate_retail_invoices(generator: DocumentGenerator, n_docs: int = 3) -> List[str]:
    """Generate synthetic retail/supermarket invoices"""
    print(f"\n=== Generating {n_docs} Retail Invoices ===")
    
    generator.generate(
        n_docs=n_docs,
        document_type="Invoice",
        audience="Retail customer",
        tone="professional",
        purpose="Generate detailed supermarket invoices with grocery and household items purchases. Include unit prices, quantities, subtotals, and tax calculations.",
        region="North America",
        language="English",
        length="Long",
        topics="Groceries, Household goods, Unit price, Quantity, Subtotals, Tax, Total due, Payment method, Store information, Receipt format",
        style_guide="Clean and readable receipt-style format typical of supermarket invoices with itemized list",
        output_dir=str(OUTPUT_DIR),
    )
    
    return list(OUTPUT_DIR.glob("*.pdf"))

def generate_bank_statements(generator: DocumentGenerator, n_docs: int = 4) -> List[str]:
    """Generate synthetic bank statements"""
    print(f"\n=== Generating {n_docs} Bank Statements ===")
    
    generator.generate(
        n_docs=n_docs,
        document_type="Bank Statement",
        audience="Account holder",
        tone="formal",
        purpose="Generate comprehensive bank statements showing account activity, transactions, balances, and account details.",
        region="North America",
        language="English",
        length="Long",
        topics="Account balance, Transactions, Deposits, Withdrawals, Fees, Interest, Account number, Statement period, Bank information",
        style_guide="Official bank statement format with clear transaction details and account summary",
        output_dir=str(OUTPUT_DIR),
    )
    
    return list(OUTPUT_DIR.glob("*.pdf"))

def main():
    """Main function to generate all synthetic documents"""
    print("🚀 Synthetic Document Generation for AI Agent Workshop")
    
    # Check license
    license_key = check_license()
    print(f"✅ License key found: {license_key[:8]}...")
    
    # Initialize generator
    print("\n📄 Initializing Document Generator...")
    generator = DocumentGenerator(document_format=DocumentFormat.PDF)
    
    # Generate different types of documents
    try:
        # Generate corporate invoices
        corporate_invoices = generate_invoices(generator, n_docs=5)
        
        # Generate retail invoices  
        retail_invoices = generate_retail_invoices(generator, n_docs=3)
        
        # Generate bank statements
        bank_statements = generate_bank_statements(generator, n_docs=4)
        
        # Summary
        all_docs = list(OUTPUT_DIR.glob("*.pdf"))
        print(f"\n✅ Successfully generated {len(all_docs)} documents:")
        print(f"   📁 Output directory: {OUTPUT_DIR.resolve()}")
        print(f"   📄 Corporate invoices: {len(corporate_invoices)}")
        print(f"   🛒 Retail invoices: {len(retail_invoices)}")
        print(f"   🏦 Bank statements: {len(bank_statements)}")
        
        print(f"\n🎯 Next steps:")
        print(f"   1. Run: python ai_agent.py")
        print(f"   2. The AI agent will process these documents and build a vector database")
        print(f"   3. Test the Q&A capabilities with various queries")
        
    except Exception as e:
        print(f"❌ Error generating documents: {e}")
        print("Please check your license key and internet connection.")
        sys.exit(1)

if __name__ == "__main__":
    main()
