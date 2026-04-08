"""
Transaction decorator and management system
Supports DS_ (standard) and NDS_ (custom) prefixes
"""

from typing import Dict, Type, Callable, Any, Optional
from functools import wraps
from dataclasses import dataclass, field
from enum import Enum


class TransactionType(str, Enum):
    CRUD = "CRUD"
    REPORT = "REPORT"
    TOOL = "TOOL"
    WORKFLOW = "WORKFLOW"
    API = "API"


@dataclass
class TransactionMetadata:
    """Metadata for a registered transaction"""
    code: str
    name: str
    group: str
    type: TransactionType
    version: str = "1.0.0"
    author: str = "system"
    description: str = ""
    permissions: list = field(default_factory=list)
    parameters: dict = field(default_factory=dict)
    is_standard: bool = True  # DS_ vs NDS_
    plugin: Optional[str] = None


class Transaction:
    """Base class for all transactions"""
    
    def __init__(self, **kwargs):
        self.params = kwargs
        self.user = None
        self.start_time = None
        self.end_time = None
        
    def execute(self) -> Any:
        """Execute the transaction - to be overridden"""
        raise NotImplementedError
    
    def get_screen(self):
        """Return the UI screen for this transaction"""
        raise NotImplementedError


class TransactionRegistry:
    """Central registry for all transactions DS_ and NDS_"""
    
    _instance: Optional['TransactionRegistry'] = None
    _transactions: Dict[str, TransactionMetadata] = {}
    _transaction_classes: Dict[str, Type[Transaction]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, metadata: TransactionMetadata, transaction_class: Type[Transaction]):
        """Register a transaction"""
        code = metadata.code
        
        # Validate prefix
        if code.startswith("DS_"):
            metadata.is_standard = True
        elif code.startswith("NDS_"):
            metadata.is_standard = False
        else:
            raise ValueError(f"Transaction code {code} must start with DS_ or NDS_")
        
        self._transactions[code] = metadata
        self._transaction_classes[code] = transaction_class
        
        return transaction_class
    
    def get_transaction(self, code: str) -> Optional[TransactionMetadata]:
        """Get transaction metadata by code"""
        return self._transactions.get(code)
    
    def get_transaction_class(self, code: str) -> Optional[Type[Transaction]]:
        """Get transaction class by code"""
        return self._transaction_classes.get(code)
    
    def get_all_transactions(self) -> Dict[str, TransactionMetadata]:
        """Get all registered transactions"""
        return self._transactions.copy()
    
    def get_standard_transactions(self) -> Dict[str, TransactionMetadata]:
        """Get only DS_ transactions"""
        return {k: v for k, v in self._transactions.items() if v.is_standard}
    
    def get_custom_transactions(self) -> Dict[str, TransactionMetadata]:
        """Get only NDS_ transactions"""
        return {k: v for k, v in self._transactions.items() if not v.is_standard}


# Global registry instance
registry = TransactionRegistry()


def transaction(
    code: str,
    name: str,
    group: str = "General",
    type: TransactionType = TransactionType.TOOL,
    version: str = "1.0.0",
    author: str = "system",
    description: str = "",
    permissions: list = None
):
    """
    Decorator to register a transaction.
    
    Transaction codes must start with:
    - DS_ for standard platform transactions
    - NDS_ for custom/user-created transactions
    """
    def decorator(cls: Type[Transaction]):
        metadata = TransactionMetadata(
            code=code,
            name=name,
            group=group,
            type=type,
            version=version,
            author=author,
            description=description,
            permissions=permissions or []
        )
        
        registry.register(metadata, cls)
        
        @wraps(cls)
        def wrapper(*args, **kwargs):
            instance = cls(*args, **kwargs)
            return instance
        
        return wrapper
    return decorator