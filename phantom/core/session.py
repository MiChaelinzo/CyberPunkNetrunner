#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Session Manager

Manages operation sessions, state persistence,
and multi-target coordination.
"""

import os
import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from enum import Enum


class SessionStatus(Enum):
    """Session status states"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass
class Target:
    """Target information container"""
    identifier: str
    target_type: str  # ip, domain, network, user, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    added_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Operation:
    """Operation record"""
    op_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    module: str = ""
    target: str = ""
    status: str = "pending"
    started_at: str = ""
    completed_at: str = ""
    results: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)


@dataclass
class Session:
    """Session data container"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Session"
    description: str = ""
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    targets: List[Target] = field(default_factory=list)
    operations: List[Operation] = field(default_factory=list)
    findings: List[Dict[str, Any]] = field(default_factory=list)
    notes: str = ""


class SessionManager:
    """
    Manages PHANTOM operation sessions
    
    Provides:
    - Session creation and management
    - State persistence
    - Target tracking
    - Operation history
    - Finding aggregation
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = storage_dir or str(Path.home() / ".phantom" / "sessions")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.current_session: Optional[Session] = None
        self._sessions_cache: Dict[str, Session] = {}
    
    def create_session(self, name: str, description: str = "") -> Session:
        """Create a new session"""
        session = Session(name=name, description=description)
        self.current_session = session
        self._sessions_cache[session.session_id] = session
        self.save_session(session)
        return session
    
    def load_session(self, session_id: str) -> Optional[Session]:
        """Load a session from storage"""
        session_file = os.path.join(self.storage_dir, f"{session_id}.json")
        
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                
                session = self._dict_to_session(data)
                self._sessions_cache[session_id] = session
                return session
            except Exception as e:
                print(f"[!] Error loading session: {e}")
        
        return None
    
    def save_session(self, session: Optional[Session] = None):
        """Save session to storage"""
        session = session or self.current_session
        if not session:
            return
        
        session.updated_at = datetime.now().isoformat()
        session_file = os.path.join(self.storage_dir, f"{session.session_id}.json")
        
        with open(session_file, 'w') as f:
            json.dump(self._session_to_dict(session), f, indent=2)
    
    def list_sessions(self) -> List[Dict[str, str]]:
        """List all available sessions"""
        sessions = []
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.storage_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    sessions.append({
                        'session_id': data.get('session_id', ''),
                        'name': data.get('name', 'Unknown'),
                        'status': data.get('status', 'unknown'),
                        'created_at': data.get('created_at', ''),
                        'updated_at': data.get('updated_at', ''),
                    })
                except Exception:
                    continue
        
        return sorted(sessions, key=lambda x: x.get('updated_at', ''), reverse=True)
    
    def add_target(self, identifier: str, target_type: str, metadata: Dict[str, Any] = None) -> Target:
        """Add a target to the current session"""
        if not self.current_session:
            self.create_session("Auto-Session")
        
        target = Target(
            identifier=identifier,
            target_type=target_type,
            metadata=metadata or {}
        )
        self.current_session.targets.append(target)
        self.save_session()
        return target
    
    def start_operation(self, module: str, target: str = "") -> Operation:
        """Start a new operation"""
        if not self.current_session:
            self.create_session("Auto-Session")
        
        operation = Operation(
            module=module,
            target=target,
            status="running",
            started_at=datetime.now().isoformat()
        )
        self.current_session.operations.append(operation)
        self.save_session()
        return operation
    
    def end_operation(self, op_id: str, success: bool, results: Dict[str, Any] = None):
        """End an operation and record results"""
        if not self.current_session:
            return
        
        for op in self.current_session.operations:
            if op.op_id == op_id:
                op.status = "success" if success else "failed"
                op.completed_at = datetime.now().isoformat()
                op.results = results or {}
                break
        
        self.save_session()
    
    def add_finding(self, category: str, severity: str, title: str, details: Dict[str, Any]):
        """Record a security finding"""
        if not self.current_session:
            self.create_session("Auto-Session")
        
        finding = {
            'id': str(uuid.uuid4())[:8],
            'category': category,
            'severity': severity,
            'title': title,
            'details': details,
            'discovered_at': datetime.now().isoformat()
        }
        self.current_session.findings.append(finding)
        self.save_session()
    
    def export_session(self, session_id: str, format: str = "json") -> str:
        """Export session in specified format"""
        session = self.load_session(session_id)
        if not session:
            return ""
        
        if format == "json":
            return json.dumps(self._session_to_dict(session), indent=2)
        elif format == "markdown":
            return self._session_to_markdown(session)
        
        return ""
    
    def _session_to_dict(self, session: Session) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            'session_id': session.session_id,
            'name': session.name,
            'description': session.description,
            'status': session.status.value if isinstance(session.status, SessionStatus) else session.status,
            'created_at': session.created_at,
            'updated_at': session.updated_at,
            'targets': [asdict(t) for t in session.targets],
            'operations': [asdict(o) for o in session.operations],
            'findings': session.findings,
            'notes': session.notes,
        }
    
    def _dict_to_session(self, data: Dict[str, Any]) -> Session:
        """Convert dictionary to session"""
        session = Session()
        session.session_id = data.get('session_id', session.session_id)
        session.name = data.get('name', '')
        session.description = data.get('description', '')
        session.status = SessionStatus(data.get('status', 'active'))
        session.created_at = data.get('created_at', '')
        session.updated_at = data.get('updated_at', '')
        session.targets = [Target(**t) for t in data.get('targets', [])]
        session.operations = [Operation(**o) for o in data.get('operations', [])]
        session.findings = data.get('findings', [])
        session.notes = data.get('notes', '')
        return session
    
    def _session_to_markdown(self, session: Session) -> str:
        """Convert session to markdown report"""
        md = f"# PHANTOM Session Report\n\n"
        md += f"**Session:** {session.name}\n"
        md += f"**ID:** {session.session_id}\n"
        md += f"**Status:** {session.status.value}\n"
        md += f"**Created:** {session.created_at}\n\n"
        
        if session.description:
            md += f"## Description\n\n{session.description}\n\n"
        
        if session.targets:
            md += "## Targets\n\n"
            for target in session.targets:
                md += f"- **{target.identifier}** ({target.target_type})\n"
            md += "\n"
        
        if session.findings:
            md += "## Findings\n\n"
            for finding in session.findings:
                md += f"### [{finding['severity']}] {finding['title']}\n"
                md += f"Category: {finding['category']}\n\n"
            md += "\n"
        
        return md
