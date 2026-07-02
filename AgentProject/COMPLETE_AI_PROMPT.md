# 🤖 COMPLETE AI IMPLEMENTATION PROMPT

> Copy this ENTIRE prompt and paste into ChatGPT/Claude

---

# MASTER PROMPT: Build EU AI Act Compliant Trial Balance Analyzer

I need you to build a complete, production-ready Trial Balance analyzer system with EU AI Act compliance. This is a comprehensive project that needs to be implemented in phases. Please implement everything step by step, showing me the code for each component.

## 🎯 PROJECT OVERVIEW

**System Name:** Trial Balance AI Analyzer  
**Purpose:** Automatically classify G/L accounts from Trial Balance Excel files  
**Technology:** Python + LangChain + OpenAI GPT-3.5-turbo  
**Compliance:** EU AI Act (HIGH RISK system)  
**Input:** Excel file with 456 G/L accounts  
**Output:** Classified accounts with audit trail  

## 📊 INPUT DATA STRUCTURE

The Excel file (`TrialBal-follow up.xlsx`) has this structure:

```
Row 0: "Отдел" (header)
Row 1: Empty
Row 2: Headers
  - Column 0: "G/L Account"
  - Column 3: Account description
  - Column 4: "Starting Balance"
  - Columns 5-10: Monthly movements (Apr-Sep 2025)
  - Column 11: "Ending Balance"

Row 3+: Account data
  Example: 10010000 | 1.0 | 10.0 | Petty Cash BGN | 1144.44 | -500 | 2050 | ... | 1124.65
```

The file contains 456 G/L accounts that need to be classified into accounting categories.

---

## 🏗️ PHASE 1: CORE SYSTEM (MVP)

### 1.1 PROJECT SETUP

Create a new Python project with this structure:

```
trial-balance-ai/
├── src/
│   ├── __init__.py
│   ├── parser.py              # Excel parser
│   ├── classifier.py          # LangChain classifier
│   ├── compliance.py          # EU compliance features
│   ├── security.py            # Security module
│   ├── monitoring.py          # Performance monitoring
│   └── exporter.py            # Results export
├── tests/
│   └── test_trial_balance.py  # Tests
├── audit_logs/                # Audit trail (created at runtime)
├── config.yaml                # Configuration
├── requirements.txt           # Dependencies
├── cli.py                     # Command-line interface
├── README.md                  # User documentation
└── .env.example               # API key template
```

**requirements.txt:**
```
pandas>=2.0.0
openpyxl>=3.1.0
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-community>=0.0.20
python-dotenv>=1.0.0
pydantic>=2.0.0
PyYAML>=6.0
tqdm>=4.65.0
pytest>=7.0.0
```

---

### 1.2 EXCEL PARSER (src/parser.py)

Create a robust Excel parser:

```python
import pandas as pd
from pathlib import Path
from typing import List, Dict
import logging

class TrialBalanceParser:
    """Parse Trial Balance Excel files"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_excel(self, file_path: str) -> List[Dict]:
        """
        Parse Trial Balance Excel file
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            List of account dictionaries with:
            - gl_account: Account number (str)
            - description: Account name (str)
            - starting_balance: Starting amount (float)
            - monthly_movements: List of 6 monthly amounts (list)
            - ending_balance: Final amount (float)
        """
        
        # Implementation:
        # 1. Read Excel without headers (header=None)
        # 2. Find data start row (row with "G/L Account" in column 0 or 3)
        # 3. Extract account data from row 3 onwards
        # 4. Handle NaN values (convert to 0)
        # 5. Validate data types
        # 6. Return list of account dictionaries
        
        # Error handling:
        # - FileNotFoundError
        # - Excel parsing errors
        # - Invalid data format
        
    def validate_account(self, account: Dict) -> bool:
        """Validate single account data"""
        # Check required fields present
        # Validate data types
        # Check balance reconciliation if possible
```

**Requirements:**
- Must parse exactly 456 accounts from the file
- Handle missing values gracefully
- Validate all numeric fields are float
- Log any parsing warnings
- Raise clear exceptions on errors

---

### 1.3 LANGCHAIN CLASSIFIER (src/classifier.py)

Create intelligent LangChain-based classifier:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Dict, List
import os

class AccountClassification(BaseModel):
    """Pydantic model for classification output"""
    category: str = Field(description="Main category: Assets, Liabilities, Equity, Revenue, or Expenses")
    subcategory: str = Field(description="Specific subcategory")
    account_type: str = Field(description="Detailed account type")
    confidence: float = Field(description="Confidence score 0.0-1.0")
    reasoning: str = Field(description="Brief explanation of classification")

class TrialBalanceClassifier:
    """LangChain-based account classifier"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        # Initialize OpenAI LLM
        # Create prompt with few-shot examples
        # Setup JSON output parser
        
    def _create_prompt(self):
        """Create comprehensive prompt with few-shot examples"""
        
        # Define categories
        categories = {
            'Assets': [
                'Cash & Cash Equivalents',
                'Bank Accounts',
                'Accounts Receivable',
                'Inventory',
                'Prepaid Expenses',
                'Fixed Assets',
                'Intangible Assets',
                'Investments',
                'Other Assets'
            ],
            'Liabilities': [
                'Accounts Payable',
                'Short-term Debt',
                'Long-term Debt',
                'Accrued Expenses',
                'Deferred Revenue',
                'Taxes Payable',
                'Other Liabilities'
            ],
            'Equity': [
                'Share Capital',
                'Retained Earnings',
                'Reserves',
                'Other Equity'
            ],
            'Revenue': [
                'Sales Revenue',
                'Service Revenue',
                'Interest Income',
                'Other Revenue'
            ],
            'Expenses': [
                'Cost of Goods Sold',
                'Salaries & Wages',
                'Rent',
                'Utilities',
                'Depreciation',
                'Marketing',
                'Travel',
                'Professional Fees',
                'Other Expenses'
            ]
        }
        
        # Few-shot examples (at least 10)
        examples = [
            {
                "input": "Account: 10010000 - Petty Cash BGN, Balance: 1124.65 BGN",
                "output": {
                    "category": "Assets",
                    "subcategory": "Cash & Cash Equivalents",
                    "account_type": "Petty Cash",
                    "confidence": 0.95,
                    "reasoning": "Petty cash is highly liquid current asset used for small expenses"
                }
            },
            {
                "input": "Account: 11001000 - DSK BGN BG41 payment bank account, Balance: -56269.21 BGN",
                "output": {
                    "category": "Assets",
                    "subcategory": "Bank Accounts",
                    "account_type": "Operating Bank Account",
                    "confidence": 0.92,
                    "reasoning": "Bank account for operational payments, negative balance indicates overdraft"
                }
            },
            {
                "input": "Account: 16004000 - Fixed Assets, Balance: 144094911.39 BGN",
                "output": {
                    "category": "Assets",
                    "subcategory": "Fixed Assets",
                    "account_type": "Property, Plant & Equipment",
                    "confidence": 0.90,
                    "reasoning": "Large balance typical for fixed assets, long-term tangible assets"
                }
            },
            # Add more examples for Liabilities, Equity, Revenue, Expenses
        ]
        
        # Create prompt template
        # System message with categories
        # Few-shot examples
        # Human message with account data
        
    def classify_account(self, account: Dict) -> Dict:
        """
        Classify single account
        
        Args:
            account: Account dictionary from parser
            
        Returns:
            Classification dictionary with category, confidence, etc.
        """
        # Format account data for prompt
        # Call LLM
        # Parse JSON output
        # Add error handling and retries
        
    def classify_batch(self, accounts: List[Dict]) -> List[Dict]:
        """Classify all accounts with progress bar"""
        from tqdm import tqdm
        
        results = []
        errors = []
        
        for account in tqdm(accounts, desc="🤖 Classifying accounts"):
            try:
                result = self.classify_account(account)
                results.append({**account, **result})
            except Exception as e:
                errors.append({"account": account, "error": str(e)})
                results.append({**account, "error": str(e)})
        
        if errors:
            print(f"⚠️  {len(errors)} errors occurred")
            
        return results
```

---

### 1.4 COMPLIANCE MODULE (src/compliance.py)

Implement EU AI Act compliance features:

```python
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

class ComplianceAuditLogger:
    """EU AI Act compliant audit logging"""
    
    def __init__(self, log_dir: str = "audit_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"audit_{timestamp}.jsonl"
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def log_classification(self, account: Dict, classification: Dict, metadata: Dict):
        """Log every classification (5 year retention)"""
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'classification',
            'account': {
                'gl_account': account.get('gl_account'),
                'description': account.get('description'),
                'ending_balance': account.get('ending_balance')
            },
            'classification': {
                'category': classification.get('category'),
                'subcategory': classification.get('subcategory'),
                'confidence': classification.get('confidence'),
                'reasoning': classification.get('reasoning')
            },
            'metadata': {
                'model_version': metadata.get('model_version', 'gpt-3.5-turbo'),
                'user_id': metadata.get('user_id'),
                'session_id': metadata.get('session_id'),
                'risk_level': metadata.get('risk_level')
            }
        }
        
        # Write to JSONL
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def log_human_override(self, original: Dict, corrected: Dict, user: str, reason: str):
        """Log human overrides"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'human_override',
            'original': original,
            'corrected': corrected,
            'user': user,
            'reason': reason
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def log_error(self, error: Exception, context: Dict):
        """Log system errors"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'error',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

class RiskAssessment:
    """Risk assessment for EU AI Act compliance"""
    
    def assess_risk(self, account: Dict, classification: Dict) -> str:
        """
        Calculate risk level: LOW, MEDIUM, HIGH
        
        Factors:
        1. Materiality (account balance)
        2. Confidence score
        3. Account complexity
        """
        
        risk_score = 0
        balance = abs(account.get('ending_balance', 0))
        confidence = classification.get('confidence', 0)
        
        # Materiality
        if balance > 1_000_000:  # 1M BGN
            risk_score += 3
        elif balance > 100_000:  # 100K BGN
            risk_score += 2
        elif balance > 10_000:   # 10K BGN
            risk_score += 1
        
        # Confidence
        if confidence < 0.7:
            risk_score += 2
        elif confidence < 0.85:
            risk_score += 1
        
        # Complexity (based on description)
        desc = account.get('description', '').lower()
        if any(word in desc for word in ['other', 'miscellaneous', 'various']):
            risk_score += 1
        
        # Classify risk
        if risk_score >= 5:
            return 'HIGH'
        elif risk_score >= 3:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def get_required_actions(self, risk_level: str) -> List[str]:
        """Get required actions based on risk"""
        if risk_level == 'HIGH':
            return ['mandatory_human_review', 'senior_approval', 'detailed_documentation']
        elif risk_level == 'MEDIUM':
            return ['recommended_review', 'spot_check']
        else:
            return ['automated_processing']

class HumanOversightModule:
    """Human oversight for HIGH RISK system"""
    
    def __init__(self):
        self.review_threshold = 0.85
    
    def requires_review(self, account: Dict, classification: Dict, risk_level: str) -> bool:
        """Determine if human review is required"""
        
        # Mandatory review for HIGH risk
        if risk_level == 'HIGH':
            return True
        
        # Low confidence
        if classification.get('confidence', 1.0) < self.review_threshold:
            return True
        
        # Classification as "Other"
        if 'other' in classification.get('subcategory', '').lower():
            return True
        
        return False
    
    def create_review_item(self, account: Dict, classification: Dict, risk_level: str) -> Dict:
        """Create review queue item"""
        return {
            'gl_account': account.get('gl_account'),
            'description': account.get('description'),
            'balance': account.get('ending_balance'),
            'ai_classification': classification,
            'risk_level': risk_level,
            'requires_review': True,
            'review_status': 'PENDING',
            'created_at': datetime.now().isoformat()
        }
```

---

### 1.5 SECURITY MODULE (src/security.py)

Implement security features:

```python
import re
from typing import Dict

class SecurityModule:
    """Security and input validation"""
    
    def __init__(self):
        self.dangerous_patterns = [
            'ignore previous instructions',
            'forget all previous',
            'system:',
            'you are now',
            '<script>',
            'DROP TABLE',
            'DELETE FROM',
            'javascript:',
            'eval(',
            'exec('
        ]
    
    def sanitize_input(self, account: Dict) -> Dict:
        """Validate and sanitize account data"""
        
        # Validate GL account format
        gl_account = str(account.get('gl_account', ''))
        if not self.validate_gl_account(gl_account):
            raise ValueError(f"Invalid GL account format: {gl_account}")
        
        # Sanitize description
        description = str(account.get('description', ''))
        
        # Check length
        if len(description) > 500:
            raise ValueError("Description too long (max 500 chars)")
        
        # Check for prompt injection
        desc_lower = description.lower()
        for pattern in self.dangerous_patterns:
            if pattern in desc_lower:
                raise SecurityError(f"Potentially harmful pattern detected: {pattern}")
        
        # Validate balance
        balance = account.get('ending_balance', 0)
        if abs(balance) > 1_000_000_000:  # 1B sanity check
            raise ValueError(f"Balance suspiciously large: {balance}")
        
        return account
    
    def validate_gl_account(self, account: str) -> bool:
        """Validate GL account format (typically 8 digits)"""
        # Allow 6-10 digit account numbers
        return bool(re.match(r'^\d{6,10}$', str(account).strip()))

class SecurityError(Exception):
    """Security-related error"""
    pass
```

---

### 1.6 RESULTS EXPORTER (src/exporter.py)

Create export functionality:

```python
import pandas as pd
from pathlib import Path
from typing import List, Dict

class ResultsExporter:
    """Export results to various formats"""
    
    def export_to_csv(self, results: List[Dict], output_path: str):
        """Export results to CSV"""
        df = pd.DataFrame(results)
        
        # Reorder columns
        columns = [
            'gl_account',
            'description',
            'starting_balance',
            'ending_balance',
            'category',
            'subcategory',
            'account_type',
            'confidence',
            'risk_level',
            'requires_review',
            'reasoning'
        ]
        
        # Keep only existing columns
        columns = [c for c in columns if c in df.columns]
        df = df[columns]
        
        # Save
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"💾 Results exported to: {output_path}")
    
    def export_to_excel(self, results: List[Dict], output_path: str):
        """Export to Excel with formatting"""
        df = pd.DataFrame(results)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Classifications')
            
            # Get worksheet
            worksheet = writer.sheets['Classifications']
            
            # Freeze header row
            worksheet.freeze_panes = 'A2'
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"💾 Results exported to: {output_path}")
    
    def generate_summary_report(self, results: List[Dict]) -> str:
        """Generate text summary report"""
        df = pd.DataFrame(results)
        
        report = []
        report.append("="*80)
        report.append("📊 TRIAL BALANCE ANALYSIS SUMMARY")
        report.append("="*80)
        
        report.append(f"\n📈 Total Accounts: {len(df)}")
        
        # By category
        report.append(f"\n📋 Accounts by Category:")
        if 'category' in df.columns:
            for cat, count in df['category'].value_counts().items():
                report.append(f"   • {cat}: {count}")
        
        # By risk
        report.append(f"\n⚠️  Accounts by Risk Level:")
        if 'risk_level' in df.columns:
            for risk, count in df['risk_level'].value_counts().items():
                report.append(f"   • {risk}: {count}")
        
        # Review required
        if 'requires_review' in df.columns:
            review_count = df['requires_review'].sum()
            report.append(f"\n👤 Accounts Requiring Human Review: {review_count}")
        
        # Average confidence
        if 'confidence' in df.columns:
            avg_confidence = df['confidence'].mean()
            report.append(f"\n🎯 Average Confidence: {avg_confidence:.1%}")
        
        # High-risk accounts
        if 'risk_level' in df.columns:
            high_risk = df[df['risk_level'] == 'HIGH']
            if len(high_risk) > 0:
                report.append(f"\n🚨 High-Risk Accounts:")
                for _, row in high_risk.head(10).iterrows():
                    report.append(f"   • {row['gl_account']} - {row['description']}: {row.get('ending_balance', 0):,.2f} BGN")
        
        report.append("\n" + "="*80)
        
        return "\n".join(report)
```

---

### 1.7 MAIN SYSTEM CLASS (src/__init__.py and main implementation)

Create unified system:

```python
from typing import Dict, List
import time
from pathlib import Path

from .parser import TrialBalanceParser
from .classifier import TrialBalanceClassifier
from .compliance import ComplianceAuditLogger, RiskAssessment, HumanOversightModule
from .security import SecurityModule
from .exporter import ResultsExporter

class TrialBalanceAISystem:
    """
    EU AI Act Compliant Trial Balance Analyzer
    Risk Classification: HIGH
    """
    
    def __init__(self, api_key: str, config: Dict = None):
        # Initialize components
        self.parser = TrialBalanceParser()
        self.classifier = TrialBalanceClassifier(api_key)
        self.audit_logger = ComplianceAuditLogger()
        self.risk_assessment = RiskAssessment()
        self.human_oversight = HumanOversightModule()
        self.security = SecurityModule()
        self.exporter = ResultsExporter()
        
        # System metadata
        self.version = "1.0.0"
        self.model = "gpt-3.5-turbo"
        
    def analyze_trial_balance(
        self,
        excel_file: str,
        user_id: str = None,
        output_file: str = None,
        summary_file: str = None
    ) -> Dict:
        """
        Main analysis pipeline
        
        Returns:
            Dict with results, summary, high-risk accounts, audit log path
        """
        
        print("🚀 Starting Trial Balance Analysis...")
        print(f"📁 File: {excel_file}")
        print(f"👤 User: {user_id or 'N/A'}")
        print()
        
        # Step 1: Parse Excel
        print("📂 Parsing Excel file...")
        accounts = self.parser.parse_excel(excel_file)
        print(f"✅ Parsed {len(accounts)} accounts\n")
        
        # Step 2: Classify accounts
        print("🤖 Classifying accounts with AI...")
        results = []
        
        for account in accounts:
            try:
                # Security check
                account = self.security.sanitize_input(account)
                
                # Classify
                start_time = time.time()
                classification = self.classifier.classify_account(account)
                response_time = time.time() - start_time
                
                # Risk assessment
                risk_level = self.risk_assessment.assess_risk(account, classification)
                
                # Human oversight check
                requires_review = self.human_oversight.requires_review(
                    account, classification, risk_level
                )
                
                # Combine results
                result = {
                    **account,
                    **classification,
                    'risk_level': risk_level,
                    'requires_review': requires_review,
                    'response_time': response_time,
                    'timestamp': time.time()
                }
                
                results.append(result)
                
                # Audit log
                self.audit_logger.log_classification(
                    account=account,
                    classification=classification,
                    metadata={
                        'user_id': user_id,
                        'risk_level': risk_level,
                        'model_version': self.model
                    }
                )
                
            except Exception as e:
                print(f"⚠️  Error classifying {account.get('gl_account')}: {e}")
                self.audit_logger.log_error(e, {'account': account})
                
                results.append({
                    **account,
                    'error': str(e),
                    'category': 'ERROR',
                    'risk_level': 'UNKNOWN'
                })
        
        print(f"✅ Classification complete!\n")
        
        # Step 3: Generate summary
        summary_text = self.exporter.generate_summary_report(results)
        print(summary_text)
        
        # Step 4: Export results
        if output_file:
            if output_file.endswith('.xlsx'):
                self.exporter.export_to_excel(results, output_file)
            else:
                self.exporter.export_to_csv(results, output_file)
        
        if summary_file:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_text)
            print(f"\n💾 Summary saved to: {summary_file}")
        
        # Step 5: Return complete analysis
        high_risk = [r for r in results if r.get('risk_level') == 'HIGH']
        needs_review = [r for r in results if r.get('requires_review')]
        
        return {
            'results': results,
            'summary': summary_text,
            'high_risk_accounts': high_risk,
            'requires_review': needs_review,
            'audit_log': str(self.audit_logger.log_file),
            'total_accounts': len(results),
            'successful': len([r for r in results if 'error' not in r]),
            'errors': len([r for r in results if 'error' in r])
        }
```

---

### 1.8 CLI INTERFACE (cli.py)

Create command-line interface:

```python
#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

from src import TrialBalanceAISystem

def main():
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="Trial Balance AI Analyzer - EU AI Act Compliant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py input.xlsx --output results.csv
  python cli.py input.xlsx -o results.xlsx --summary summary.txt
  python cli.py input.xlsx --api-key YOUR_KEY
        """
    )
    
    parser.add_argument(
        "input_file",
        help="Path to Trial Balance Excel file"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file path (CSV or Excel)",
        default="results.csv"
    )
    
    parser.add_argument(
        "--summary", "-s",
        help="Summary report file path",
        default=None
    )
    
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (or set OPENAI_API_KEY env var)",
        default=None
    )
    
    parser.add_argument(
        "--user-id",
        help="User ID for audit trail",
        default=None
    )
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OpenAI API key required!")
        print("   Set OPENAI_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    # Check input file exists
    if not Path(args.input_file).exists():
        print(f"❌ Error: File not found: {args.input_file}")
        sys.exit(1)
    
    try:
        # Create system
        system = TrialBalanceAISystem(api_key=api_key)
        
        # Run analysis
        result = system.analyze_trial_balance(
            excel_file=args.input_file,
            user_id=args.user_id,
            output_file=args.output,
            summary_file=args.summary
        )
        
        # Final summary
        print("\n" + "="*80)
        print("🎉 ANALYSIS COMPLETE!")
        print("="*80)
        print(f"✅ Total accounts: {result['total_accounts']}")
        print(f"✅ Successful: {result['successful']}")
        if result['errors'] > 0:
            print(f"⚠️  Errors: {result['errors']}")
        print(f"🚨 High-risk accounts: {len(result['high_risk_accounts'])}")
        print(f"👤 Requires review: {len(result['requires_review'])}")
        print(f"📋 Results: {args.output}")
        print(f"📝 Audit log: {result['audit_log']}")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

### 1.9 CONFIGURATION (config.yaml)

Create configuration file:

```yaml
system:
  name: "Trial Balance AI Analyzer"
  version: "1.0.0"
  compliance: "EU AI Act - HIGH RISK"
  description: "Automated G/L account classification system"

openai:
  model: "gpt-3.5-turbo"
  temperature: 0.1
  max_retries: 3
  timeout: 30

risk_assessment:
  high_risk_threshold: 1000000  # 1M BGN
  medium_risk_threshold: 100000  # 100K BGN
  low_confidence_threshold: 0.85

human_oversight:
  mandatory_review_for_high_risk: true
  review_threshold_confidence: 0.85
  flag_uncertain_classifications: true

audit:
  log_directory: "audit_logs"
  retention_years: 5
  log_format: "jsonl"
  include_full_reasoning: true

security:
  enable_input_validation: true
  enable_prompt_injection_detection: true
  max_description_length: 500
  max_balance_sanity_check: 1000000000  # 1B BGN

export:
  default_format: "csv"
  include_summary_report: true
  auto_generate_timestamp: true
```

---

### 1.10 DOCUMENTATION (README.md)

Create comprehensive README:

```markdown
# 🤖 Trial Balance AI Analyzer

EU AI Act compliant system for automatic G/L account classification.

## ⚠️ EU AI Act Classification: HIGH RISK

This system is classified as HIGH RISK under EU AI Act because it:
- Operates in regulated financial/accounting sector
- Influences financial reporting and decisions
- Requires mandatory human oversight

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
echo "OPENAI_API_KEY=your-key-here" > .env
```

### Usage

```bash
# Basic usage
python cli.py trial_balance.xlsx --output results.csv

# With summary report
python cli.py trial_balance.xlsx -o results.xlsx --summary summary.txt

# Specify API key directly
python cli.py trial_balance.xlsx --api-key YOUR_KEY
```

### Python API

```python
from src import TrialBalanceAISystem

# Create system
system = TrialBalanceAISystem(api_key="your-key")

# Analyze
result = system.analyze_trial_balance(
    excel_file="trial_balance.xlsx",
    output_file="results.csv",
    user_id="accountant@company.com"
)

# Access results
print(f"High-risk accounts: {len(result['high_risk_accounts'])}")
print(f"Requires review: {len(result['requires_review'])}")
```

## 📊 Output

The system produces:

1. **Classification Results** (CSV/Excel)
   - GL Account number
   - Description
   - Balances
   - Category, Subcategory, Type
   - Confidence score
   - Risk level
   - Review flag
   - Reasoning

2. **Summary Report** (Text)
   - Total accounts by category
   - Risk distribution
   - Accounts requiring review
   - Average confidence

3. **Audit Log** (JSONL)
   - Every classification logged
   - 5-year retention
   - EU AI Act compliant

## 🇪🇺 EU AI Act Compliance

This system implements:

- ✅ Risk Management System
- ✅ Comprehensive Audit Logging
- ✅ Human Oversight (mandatory for high-risk)
- ✅ Input Validation & Security
- ✅ Performance Monitoring
- ✅ Transparency & Explainability

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Excel file with Trial Balance data

## 🔒 Security

- Input sanitization
- Prompt injection detection
- Rate limiting ready
- Secure API key handling

## 📞 Support

For issues or questions, contact: [your-email]

## 📄 License

[Your License]
```

---

### 1.11 TESTS (tests/test_trial_balance.py)

Create test suite:

```python
import pytest
from src.parser import TrialBalanceParser
from src.classifier import TrialBalanceClassifier
from src.compliance import RiskAssessment, HumanOversightModule
from src.security import SecurityModule

# Test data
SAMPLE_ACCOUNT = {
    'gl_account': '10010000',
    'description': 'Petty Cash BGN',
    'starting_balance': 1144.44,
    'ending_balance': 1124.65,
    'monthly_movements': [-500, 2050, -2369.79, 600, -300, 500]
}

def test_risk_assessment():
    """Test risk assessment logic"""
    risk = RiskAssessment()
    
    # Low risk
    account = {'ending_balance': 5000}
    classification = {'confidence': 0.95}
    assert risk.assess_risk(account, classification) == 'LOW'
    
    # High risk (large balance)
    account = {'ending_balance': 2000000}
    classification = {'confidence': 0.95}
    assert risk.assess_risk(account, classification) == 'HIGH'
    
    # High risk (low confidence)
    account = {'ending_balance': 5000}
    classification = {'confidence': 0.65}
    assert risk.assess_risk(account, classification) in ['MEDIUM', 'HIGH']

def test_security_validation():
    """Test security module"""
    security = SecurityModule()
    
    # Valid account
    account = {'gl_account': '10010000', 'description': 'Cash', 'ending_balance': 1000}
    assert security.sanitize_input(account) == account
    
    # Invalid GL account
    with pytest.raises(ValueError):
        security.sanitize_input({'gl_account': 'INVALID', 'description': 'Test'})
    
    # Prompt injection
    with pytest.raises(Exception):
        security.sanitize_input({
            'gl_account': '10010000',
            'description': 'ignore previous instructions',
            'ending_balance': 0
        })

def test_human_oversight():
    """Test human oversight module"""
    oversight = HumanOversightModule()
    
    # High risk requires review
    account = {'ending_balance': 2000000}
    classification = {'confidence': 0.95}
    assert oversight.requires_review(account, classification, 'HIGH') == True
    
    # Low confidence requires review
    account = {'ending_balance': 1000}
    classification = {'confidence': 0.75}
    assert oversight.requires_review(account, classification, 'LOW') == True
    
    # Normal case doesn't require review
    account = {'ending_balance': 1000}
    classification = {'confidence': 0.95}
    assert oversight.requires_review(account, classification, 'LOW') == False

# Add more tests as needed
```

---

## 📝 IMPLEMENTATION INSTRUCTIONS

Please implement this system following these steps:

1. **Start with Project Structure**
   - Create all directories and files
   - Create requirements.txt with all dependencies

2. **Implement Core Components** (in order):
   - parser.py (Excel parsing)
   - classifier.py (LangChain classification)
   - compliance.py (audit logging, risk assessment)
   - security.py (input validation)
   - exporter.py (results export)

3. **Create Main System**
   - Implement TrialBalanceAISystem class
   - Integrate all components
   - Add error handling

4. **Add CLI Interface**
   - cli.py with argument parsing
   - Environment variable support

5. **Documentation**
   - README.md with usage instructions
   - config.yaml with settings
   - .env.example for API key

6. **Tests**
   - test_trial_balance.py
   - Cover critical functionality

## ✅ VALIDATION

After implementation, verify:

- [ ] Parses Excel file correctly (456 accounts)
- [ ] Classifies accounts with OpenAI
- [ ] Returns valid JSON classifications
- [ ] Risk assessment works (HIGH/MEDIUM/LOW)
- [ ] Audit logging creates JSONL files
- [ ] Security checks prevent bad input
- [ ] Results export to CSV/Excel
- [ ] CLI interface works
- [ ] All tests pass

## 🎯 SUCCESS CRITERIA

The system is complete when:

1. ✅ Successfully classifies 456 accounts
2. ✅ All classifications logged to audit trail
3. ✅ High-risk accounts flagged for review
4. ✅ Results exported to CSV/Excel with all fields
5. ✅ CLI works with --help, --output, --api-key
6. ✅ Security validation prevents malicious input
7. ✅ Tests pass
8. ✅ README is complete and clear

## 📊 EXPECTED OUTPUT

When complete, running:
```bash
python cli.py trial_balance.xlsx --output results.csv --summary summary.txt
```

Should produce:
- ✅ results.csv with 456 classified accounts
- ✅ summary.txt with statistics
- ✅ audit_logs/audit_TIMESTAMP.jsonl with all classifications
- ✅ Console output showing progress and summary

---

## 🚀 START IMPLEMENTATION NOW

Please begin implementing this system. Start with:

1. Create project structure
2. Show me requirements.txt
3. Implement parser.py first
4. Test parser with sample data structure
5. Then move to classifier.py
6. Continue through all components

Show me the code for each file as you create it. Test each component before moving to the next. Let me know if you need any clarification!




