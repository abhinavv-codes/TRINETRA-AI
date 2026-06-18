"""Evidence storage - save and hash evidence images"""

import logging
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


class EvidenceManager:
    """Manage evidence images with tamper-detection"""
    
    def hash_evidence(self, image_bytes: bytes, prev_hash: str = None) -> str:
        """
        Generate SHA-256 hash of evidence
        
        Args:
            image_bytes: Image binary data
            prev_hash: Previous hash (for chain)
        
        Returns:
            SHA-256 hash hex string
        """
        
        if prev_hash:
            combined = image_bytes + prev_hash.encode()
        else:
            combined = image_bytes
        
        return hashlib.sha256(combined).hexdigest()
    
    def create_evidence_record(
        self,
        violation_id: str,
        image_bytes: bytes,
        prev_hash: str = None,
        metadata: dict = None
    ) -> Dict:
        """
        Create tamper-evident evidence record
        
        Args:
            violation_id: Associated violation ID
            image_bytes: Image binary data
            prev_hash: Previous hash for chain
            metadata: Additional metadata
        
        Returns:
            Evidence record dict with hash and chain
        """
        
        # Generate hash chain
        image_hash = self.hash_evidence(image_bytes, prev_hash)
        
        return {
            "violation_id": violation_id,
            "sha256": image_hash,
            "prev_hash": prev_hash,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
    
    def verify_evidence_chain(self, records: list) -> bool:
        """Verify integrity of evidence chain"""
        
        for i in range(len(records)):
            if i == 0:
                continue
            
            current = records[i]
            previous = records[i-1]
            
            if current.get('prev_hash') != previous.get('sha256'):
                logger.warning(f"Chain break detected at record {i}")
                return False
        
        return True
