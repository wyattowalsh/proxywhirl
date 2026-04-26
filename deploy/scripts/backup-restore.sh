#!/bin/bash
set -euo pipefail

# ProxyWhirl Backup & Restore Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups}"
DB_PATH="${DB_PATH:-$PROJECT_DIR/proxywhirl.db}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

backup() {
    log_info "Starting database backup..."
    
    mkdir -p "$BACKUP_DIR"
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/proxywhirl_$timestamp.db.gz"
    
    # Create backup
    if gzip -c "$DB_PATH" > "$backup_file"; then
        log_info "✓ Backup created: $backup_file"
        echo "$backup_file"
    else
        log_error "Backup failed"
        exit 1
    fi
    
    # Clean old backups
    find "$BACKUP_DIR" -name "proxywhirl_*.db.gz" -mtime "+$RETENTION_DAYS" -delete
    log_info "Cleaned backups older than $RETENTION_DAYS days"
}

restore() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    log_info "Restoring from backup: $backup_file"
    
    # Create backup of current database
    cp "$DB_PATH" "$DB_PATH.backup.$(date +%s)"
    
    # Restore
    if gunzip -c "$backup_file" > "$DB_PATH"; then
        log_info "✓ Restore complete"
    else
        log_error "Restore failed"
        exit 1
    fi
}

list_backups() {
    log_info "Available backups:"
    ls -lh "$BACKUP_DIR"/proxywhirl_*.db.gz 2>/dev/null | awk '{print $9, "(" $5 ")"}'
}

upload_s3() {
    local backup_file="$1"
    local s3_bucket="${S3_BUCKET:-proxywhirl-backups}"
    
    log_info "Uploading to S3: s3://$s3_bucket/$(basename "$backup_file")"
    
    if aws s3 cp "$backup_file" "s3://$s3_bucket/" --no-progress; then
        log_info "✓ Upload complete"
    else
        log_error "S3 upload failed"
        exit 1
    fi
}

case "${1:-}" in
    backup)
        backup
        ;;
    restore)
        if [ -z "${2:-}" ]; then
            log_error "Usage: $0 restore <backup_file>"
            exit 1
        fi
        restore "$2"
        ;;
    list)
        list_backups
        ;;
    *)
        echo "Usage: $0 {backup|restore|list}"
        exit 1
        ;;
esac
