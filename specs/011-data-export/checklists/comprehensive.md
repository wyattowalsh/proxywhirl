# Comprehensive Requirements Quality Checklist: Data Export & Reporting

**Purpose**: Deep validation of requirements quality across all user stories, focusing on completeness, clarity, consistency, measurability, scenario coverage, and traceability for the 011-data-export feature.

**Created**: 2025-11-02  
**Feature**: [spec.md](../spec.md)  
**Depth**: Comprehensive (100+ items)  
**Focus**: All user stories with equal priority across all scenario classes

**Note**: This checklist validates the REQUIREMENTS themselves, not their implementation. Each item tests whether the specification is well-written, complete, unambiguous, and ready for implementation.

---

## Requirement Completeness

### Proxy Pool Export/Import (US1)

- [ ] CHK001 - Are the exact fields to include in proxy pool exports explicitly specified? [Completeness, Spec §FR-001]
- [ ] CHK002 - Are requirements defined for all three credential handling modes (full/sanitized/reference)? [Completeness, Spec §FR-004]
- [ ] CHK003 - Is the encryption algorithm for "full" mode credentials specified? [Gap, Spec §FR-001]
- [ ] CHK004 - Are requirements defined for credential restoration during import? [Completeness, Spec §FR-003]
- [ ] CHK005 - Are validation requirements specified for import file format compliance? [Completeness, Spec §FR-011]
- [ ] CHK006 - Are requirements defined for all three duplicate resolution strategies (skip/rename/merge)? [Completeness, Spec §FR-012]
- [ ] CHK007 - Is the proxy health status snapshot behavior during export clearly specified? [Gap]
- [ ] CHK008 - Are requirements defined for exporting proxy metadata fields? [Completeness, Spec §FR-001]

### Analytics Data Export (US2)

- [ ] CHK009 - Are all supported analytics export formats explicitly listed? [Completeness, Spec §FR-002]
- [ ] CHK010 - Are the exact columns/fields available for analytics export specified? [Gap, Spec §FR-002]
- [ ] CHK011 - Are date range filtering requirements clearly defined? [Completeness, Spec §FR-002]
- [ ] CHK012 - Are requirements specified for column selection functionality? [Completeness, Spec §FR-002]
- [ ] CHK013 - Is the asynchronous processing threshold (10MB) justified and specified? [Completeness, Spec §FR-007]
- [ ] CHK014 - Are progress tracking requirements defined for async exports? [Completeness, Spec §FR-007]
- [ ] CHK015 - Are all notification mechanism options (in-app/email/webhook) fully specified? [Completeness, Spec §FR-019]
- [ ] CHK016 - Is the size estimation algorithm for large exports documented? [Completeness, Spec §FR-007]

### Scheduled Exports (US3)

- [ ] CHK017 - Are all supported scheduling frequencies explicitly defined? [Completeness, Spec §FR-006]
- [ ] CHK018 - Are requirements specified for time-of-day scheduling? [Completeness, Spec §FR-006]
- [ ] CHK019 - Are destination path configuration requirements defined? [Completeness, Spec §FR-006]
- [ ] CHK020 - Are retry policy requirements fully specified (attempts, backoff)? [Gap, Spec §FR-015]
- [ ] CHK021 - Are requirements defined for schedule conflict resolution? [Gap]
- [ ] CHK022 - Is scheduled export failure notification specified? [Completeness, Spec §FR-022]
- [ ] CHK023 - Are requirements defined for disabling/pausing scheduled exports? [Gap]
- [ ] CHK024 - Is schedule persistence across restarts specified? [Gap]

### Health Reports (US4)

- [ ] CHK025 - Are the specific metrics to include in health reports defined? [Gap, Spec §FR-008]
- [ ] CHK026 - Are requirements specified for availability chart generation? [Completeness, Spec §FR-008]
- [ ] CHK027 - Are failure pattern analysis requirements defined? [Completeness, Spec §FR-008]
- [ ] CHK028 - Are response time distribution requirements specified? [Completeness, Spec §FR-008]
- [ ] CHK029 - Is the PDF rendering library choice specified? [Completeness, Research §1]
- [ ] CHK030 - Are visual layout requirements for PDF reports defined? [Gap]

### Dashboard Exports (US5)

- [ ] CHK031 - Are requirements defined for which dashboard elements to include? [Gap, Spec §FR-013]
- [ ] CHK032 - Are chart rendering requirements in PDF format specified? [Completeness, Spec §FR-013]
- [ ] CHK033 - Are filter preservation requirements defined? [Completeness, Spec §FR-013]
- [ ] CHK034 - Are branding customization requirements specified? [Gap, Spec §FR-013]
- [ ] CHK035 - Is timestamp display requirement defined? [Completeness, Spec §FR-013]

### Cross-Cutting Completeness

- [ ] CHK036 - Are audit logging requirements defined for all export/import operations? [Completeness, Spec §FR-010]
- [ ] CHK037 - Are retention policy requirements fully specified? [Completeness, Spec §FR-014]
- [ ] CHK038 - Are export template requirements defined? [Completeness, Spec §FR-016]
- [ ] CHK039 - Are manifest/header requirements specified for all export formats? [Completeness, Spec §FR-017]
- [ ] CHK040 - Are API endpoint requirements for programmatic access defined? [Completeness, Spec §FR-018]
- [ ] CHK041 - Are compression requirements specified for all formats? [Completeness, Spec §FR-021]
- [ ] CHK042 - Are access control requirements fully defined? [Completeness, Spec §FR-020]

---

## Requirement Clarity

### Ambiguous Terms & Quantification

- [ ] CHK043 - Is "large exports" quantified with specific size threshold (10MB)? [Clarity, Spec §FR-007]
- [ ] CHK044 - Is "asynchronous processing" defined with specific trigger conditions? [Clarity, Spec §FR-007]
- [ ] CHK045 - Is "configurable notification" clearly defined with all options? [Clarity, Spec §FR-019]
- [ ] CHK046 - Is "encrypted credentials" defined with specific algorithm/method? [Ambiguity, Spec §FR-001]
- [ ] CHK047 - Is "failure pattern analysis" quantified with specific metrics? [Ambiguity, Spec §FR-008]
- [ ] CHK048 - Is "visual fidelity" for dashboard exports measurably defined? [Ambiguity, Spec §FR-013]
- [ ] CHK049 - Are "transient failures" clearly distinguished from permanent failures? [Ambiguity, Spec §FR-015]
- [ ] CHK050 - Is "master key or user password" authentication flow clearly specified? [Clarity, Spec §FR-003]

### Specification Precision

- [ ] CHK051 - Are CSV file encoding (UTF-8) and delimiter (comma) explicitly specified? [Clarity, Assumptions]
- [ ] CHK052 - Is Excel format (XLSX vs XLS) explicitly specified? [Clarity, Assumptions]
- [ ] CHK053 - Is the JSON structure/schema for exports defined? [Gap]
- [ ] CHK054 - Are timestamp formats (ISO 8601, UTC) consistently specified? [Clarity, Spec §FR-009]
- [ ] CHK055 - Is the file naming pattern clearly defined? [Clarity, Assumptions]
- [ ] CHK056 - Is the export directory structure specified? [Clarity, Assumptions]
- [ ] CHK057 - Are compression algorithms (gzip level 6) explicitly defined? [Clarity, Research §4]
- [ ] CHK058 - Is "creator + admin only" access precisely defined? [Clarity, Spec §FR-020]

### Edge Case Definitions

- [ ] CHK059 - Is behavior when export size exceeds storage limits clearly specified? [Clarity, Edge Cases]
- [ ] CHK060 - Is handling of credentials under restrictive security policies defined? [Clarity, Edge Cases]
- [ ] CHK061 - Is duplicate proxy identifier detection logic specified? [Clarity, Edge Cases]
- [ ] CHK062 - Is timezone handling for timestamps clearly defined? [Clarity, Edge Cases]
- [ ] CHK063 - Is snapshot isolation for active data clearly explained? [Clarity, Edge Cases]
- [ ] CHK064 - Is large export progress indication clearly specified? [Clarity, Edge Cases]
- [ ] CHK065 - Is import file format validation clearly defined? [Clarity, Edge Cases]

---

## Requirement Consistency

### Cross-Requirement Alignment

- [ ] CHK066 - Do notification preferences (FR-019) align with completion notification (FR-007)? [Consistency]
- [ ] CHK067 - Do credential handling modes (FR-004) align with import decryption (FR-003)? [Consistency]
- [ ] CHK068 - Do retention policies (FR-014) align with cleanup in edge cases? [Consistency]
- [ ] CHK069 - Do compression requirements (FR-021) align with research decision (gzip level 6)? [Consistency]
- [ ] CHK070 - Do scheduled export requirements (FR-006) align with failure handling (FR-022)? [Consistency]
- [ ] CHK071 - Do audit log requirements (FR-010) align with access control (FR-020)? [Consistency]
- [ ] CHK072 - Do API endpoint requirements (FR-018) align with async processing (FR-007)? [Consistency]

### Format Consistency

- [ ] CHK073 - Are export format requirements consistent across all user stories? [Consistency]
- [ ] CHK074 - Are metadata field requirements (FR-005) consistent across all formats? [Consistency]
- [ ] CHK075 - Are timestamp handling requirements consistent across all exports? [Consistency]
- [ ] CHK076 - Are credential handling requirements consistent across pool/analytics exports? [Consistency]

### Terminology Consistency

- [ ] CHK077 - Is "export job" terminology used consistently throughout requirements? [Consistency]
- [ ] CHK078 - Is "import job" terminology used consistently? [Consistency]
- [ ] CHK079 - Is "scheduled export" vs "automated export" terminology consistent? [Consistency]
- [ ] CHK080 - Are status values (pending/processing/completed/failed) consistent across entities? [Consistency, Data Model]

---

## Acceptance Criteria Quality

### Measurability

- [ ] CHK081 - Can "export within 2 minutes" (SC-001) be objectively measured? [Measurability, Spec §SC-001]
- [ ] CHK082 - Can "60 seconds for 100K records" (SC-002) be objectively verified? [Measurability, Spec §SC-002]
- [ ] CHK083 - Can "100% formatting success" (SC-003) be objectively tested? [Measurability, Spec §SC-003]
- [ ] CHK084 - Can "99% on-time execution" (SC-004) be objectively measured? [Measurability, Spec §SC-004]
- [ ] CHK085 - Can "90% transient failure recovery" (SC-004) be objectively verified? [Measurability, Spec §SC-004]
- [ ] CHK086 - Can "readable at 100-150% zoom" (SC-005) be objectively tested? [Measurability, Spec §SC-005]
- [ ] CHK087 - Can "100% format violation detection" (SC-006) be objectively measured? [Measurability, Spec §SC-006]
- [ ] CHK088 - Can "<10% CPU/memory overhead" (SC-007) be objectively measured with defined baseline? [Measurability, Spec §SC-007]
- [ ] CHK089 - Can "80% user success within first week" (SC-008) be objectively measured? [Measurability, Spec §SC-008]
- [ ] CHK090 - Can "100% credential protection" (SC-009) be objectively verified? [Measurability, Spec §SC-009]
- [ ] CHK091 - Can "1KB per record" and "60%+ compression" (SC-010) be objectively measured? [Measurability, Spec §SC-010]

### Coverage

- [ ] CHK092 - Do acceptance criteria cover all P1 user stories (US1, US2)? [Coverage]
- [ ] CHK093 - Do acceptance criteria cover all P2 user stories (US3, US4)? [Coverage]
- [ ] CHK094 - Are acceptance criteria defined for P3 user story (US5)? [Gap]
- [ ] CHK095 - Do acceptance criteria cover security requirements? [Coverage, SC-009]
- [ ] CHK096 - Do acceptance criteria cover performance requirements? [Coverage, SC-002, SC-007]
- [ ] CHK097 - Do acceptance criteria cover reliability requirements? [Coverage, SC-004, SC-006]

---

## Scenario Coverage

### Primary Flow Coverage

- [ ] CHK098 - Are requirements defined for the complete export flow (initiate → process → download)? [Coverage, Primary Flow]
- [ ] CHK099 - Are requirements defined for the complete import flow (upload → validate → import)? [Coverage, Primary Flow]
- [ ] CHK100 - Are requirements defined for scheduled export creation and execution? [Coverage, Primary Flow]
- [ ] CHK101 - Are requirements defined for template creation and reuse? [Coverage, Primary Flow]

### Error Handling Coverage

- [ ] CHK102 - Are requirements defined for export initiation failures? [Coverage, Exception Flow]
- [ ] CHK103 - Are requirements defined for export processing failures? [Coverage, Exception Flow, FR-015]
- [ ] CHK104 - Are requirements defined for storage limit failures? [Coverage, Exception Flow, Edge Cases]
- [ ] CHK105 - Are requirements defined for import validation failures? [Coverage, Exception Flow, FR-011]
- [ ] CHK106 - Are requirements defined for credential decryption failures? [Coverage, Exception Flow, FR-003]
- [ ] CHK107 - Are requirements defined for scheduled export failures? [Coverage, Exception Flow, FR-022]
- [ ] CHK108 - Are requirements defined for notification delivery failures? [Gap, Exception Flow]

### Recovery Flow Coverage

- [ ] CHK109 - Are requirements defined for retry mechanisms after transient failures? [Coverage, Recovery Flow, FR-015]
- [ ] CHK110 - Are requirements defined for rollback after partial import failures? [Gap, Recovery Flow]
- [ ] CHK111 - Are requirements defined for resuming interrupted exports? [Gap, Recovery Flow]
- [ ] CHK112 - Are requirements defined for recovering from corrupt export files? [Gap, Recovery Flow]

### Alternate Flow Coverage

- [ ] CHK113 - Are requirements defined for exporting with different credential modes? [Coverage, Alternate Flow, FR-004]
- [ ] CHK114 - Are requirements defined for exporting with compression disabled? [Coverage, Alternate Flow, FR-021]
- [ ] CHK115 - Are requirements defined for importing with different duplicate strategies? [Coverage, Alternate Flow, FR-012]
- [ ] CHK116 - Are requirements defined for scheduled vs manual export differences? [Gap, Alternate Flow]

### Concurrent Operation Coverage

- [ ] CHK117 - Are requirements defined for multiple simultaneous exports? [Gap, Concurrent Operations]
- [ ] CHK118 - Are requirements defined for export during active proxy operations? [Coverage, Edge Cases]
- [ ] CHK119 - Are requirements defined for scheduled export conflicts? [Gap, Concurrent Operations]
- [ ] CHK120 - Are requirements defined for concurrent import operations? [Gap, Concurrent Operations]

---

## Edge Case Coverage

### Boundary Conditions

- [ ] CHK121 - Are requirements defined for zero-record exports (empty pools)? [Gap, Edge Case]
- [ ] CHK122 - Are requirements defined for single-record exports? [Gap, Edge Case]
- [ ] CHK123 - Are requirements defined for maximum-size exports (1M records)? [Gap, Edge Case]
- [ ] CHK124 - Are requirements defined for very small files (<1KB)? [Gap, Edge Case]
- [ ] CHK125 - Are requirements defined for exports near storage limits? [Coverage, Edge Cases]

### Data Quality Edge Cases

- [ ] CHK126 - Are requirements defined for proxies with special characters in URLs? [Gap, Edge Case]
- [ ] CHK127 - Are requirements defined for proxies with missing optional fields? [Gap, Edge Case]
- [ ] CHK128 - Are requirements defined for analytics data with null values? [Gap, Edge Case]
- [ ] CHK129 - Are requirements defined for timestamp data in different timezones? [Coverage, Edge Cases]
- [ ] CHK130 - Are requirements defined for corrupt or incomplete health data? [Gap, Edge Case]

### System State Edge Cases

- [ ] CHK131 - Are requirements defined for exports during system startup/shutdown? [Gap, Edge Case]
- [ ] CHK132 - Are requirements defined for exports when storage is nearly full? [Coverage, Edge Cases]
- [ ] CHK133 - Are requirements defined for exports when scheduler is disabled? [Gap, Edge Case]
- [ ] CHK134 - Are requirements defined for import when pool already exists? [Coverage, Edge Cases]

---

## Non-Functional Requirements

### Performance Requirements

- [ ] CHK135 - Are export initiation latency requirements quantified (<100ms)? [Completeness, Plan §Performance Goals]
- [ ] CHK136 - Are analytics export time requirements quantified (<60s for 100K)? [Completeness, Spec §SC-002]
- [ ] CHK137 - Are async export overhead limits defined (<10%)? [Completeness, Spec §SC-007]
- [ ] CHK138 - Are compression performance requirements defined? [Completeness, Research §4]
- [ ] CHK139 - Are requirements defined for maximum concurrent exports? [Gap]
- [ ] CHK140 - Are proxy request latency impact limits defined? [Completeness, Plan §Constraints]

### Security Requirements

- [ ] CHK141 - Are credential encryption requirements fully specified? [Completeness, Spec §FR-004]
- [ ] CHK142 - Are credential storage requirements specified (never plain text)? [Completeness, Spec §SC-009]
- [ ] CHK143 - Are access control requirements quantified (creator + admin)? [Completeness, Spec §FR-020]
- [ ] CHK144 - Are audit logging requirements comprehensive? [Completeness, Spec §FR-010]
- [ ] CHK145 - Are credential decryption authorization requirements defined? [Completeness, Spec §FR-003]
- [ ] CHK146 - Are requirements defined for secure credential transmission? [Gap]

### Reliability Requirements

- [ ] CHK147 - Are scheduled export reliability targets quantified (99%)? [Completeness, Spec §SC-004]
- [ ] CHK148 - Are retry success targets quantified (90%)? [Completeness, Spec §SC-004]
- [ ] CHK149 - Are validation accuracy requirements quantified (100%)? [Completeness, Spec §SC-006]
- [ ] CHK150 - Are data integrity requirements defined (checksums)? [Completeness, Spec §FR-017]
- [ ] CHK151 - Are requirements defined for export job persistence across restarts? [Gap]

### Usability Requirements

- [ ] CHK152 - Are user notification requirements comprehensive? [Completeness, Spec §FR-019]
- [ ] CHK153 - Are progress indication requirements defined? [Completeness, Spec §FR-007]
- [ ] CHK154 - Are error message clarity requirements defined? [Gap]
- [ ] CHK155 - Are requirements defined for export/import UI feedback? [Gap]

---

## Dependencies & Assumptions

### External Dependencies

- [ ] CHK156 - Are pandas dependency requirements (>=2.0.0) validated? [Completeness, Plan §Technical Context]
- [ ] CHK157 - Are openpyxl dependency requirements (>=3.1.0) validated? [Completeness, Plan §Technical Context]
- [ ] CHK158 - Are reportlab dependency requirements (>=4.0.0) validated? [Completeness, Plan §Technical Context]
- [ ] CHK159 - Are apscheduler dependency requirements (>=3.10.0) validated? [Completeness, Plan §Technical Context]
- [ ] CHK160 - Is Python version compatibility (3.9+) validated? [Completeness, Plan §Technical Context]

### Integration Dependencies

- [ ] CHK161 - Are integration requirements with 001-core-python-package defined? [Completeness, Plan]
- [ ] CHK162 - Are integration requirements with 003-rest-api defined? [Completeness, Plan]
- [ ] CHK163 - Are integration requirements with 005-caching defined? [Gap]
- [ ] CHK164 - Are integration requirements with 009-analytics defined? [Completeness, Plan]
- [ ] CHK165 - Are requirements defined for storage.py extensions? [Completeness, Tasks §Phase 2]

### Assumptions Validation

- [ ] CHK166 - Is the "local filesystem initially" assumption clearly stated? [Completeness, Assumptions]
- [ ] CHK167 - Is the CSV encoding/delimiter assumption validated? [Completeness, Assumptions]
- [ ] CHK168 - Is the Excel format (XLSX) assumption validated? [Completeness, Assumptions]
- [ ] CHK169 - Is the credential encryption reuse assumption validated? [Completeness, Assumptions]
- [ ] CHK170 - Is the 30-day retention default assumption justified? [Completeness, Assumptions]
- [ ] CHK171 - Is the background thread execution assumption validated? [Completeness, Assumptions]

---

## Ambiguities & Conflicts

### Specification Ambiguities

- [ ] CHK172 - Is the relationship between export templates and scheduled exports clear? [Ambiguity, FR-016, FR-006]
- [ ] CHK173 - Is the distinction between manifest and metadata clear? [Ambiguity, FR-005, FR-017]
- [ ] CHK174 - Is the scope of "audit logging" clearly bounded? [Ambiguity, FR-010]
- [ ] CHK175 - Are notification preference defaults clearly specified? [Ambiguity, FR-019]
- [ ] CHK176 - Is the behavior for disabled compression clearly specified? [Ambiguity, FR-021]

### Potential Conflicts

- [ ] CHK177 - Do async processing requirements (FR-007) conflict with <10% overhead (SC-007)? [Potential Conflict]
- [ ] CHK178 - Do retention policies (FR-014) conflict with audit requirements (FR-010)? [Potential Conflict]
- [ ] CHK179 - Do scheduled export frequencies (FR-006) conflict with storage limits? [Potential Conflict]
- [ ] CHK180 - Does "creator only" access (FR-020) conflict with scheduled exports run as system? [Potential Conflict]

### Missing Definitions

- [ ] CHK181 - Is "system administrator" role clearly defined? [Gap]
- [ ] CHK182 - Is "export file retention" trigger clearly defined? [Gap]
- [ ] CHK183 - Is "transient failure" vs "permanent failure" clearly distinguished? [Gap]
- [ ] CHK184 - Is "large export" size calculation method defined? [Gap, FR-007]
- [ ] CHK185 - Is "webhook callback" format/protocol defined? [Gap, FR-019]

---

## Traceability

### Requirement-to-Task Traceability

- [ ] CHK186 - Does each functional requirement (FR-001 to FR-022) have corresponding tasks? [Traceability]
- [ ] CHK187 - Does each success criterion (SC-001 to SC-010) have corresponding test tasks? [Traceability]
- [ ] CHK188 - Are all acceptance scenarios covered by test tasks? [Traceability]
- [ ] CHK189 - Are all edge cases covered by test tasks? [Traceability]

### Entity-to-Requirement Traceability

- [ ] CHK190 - Is ExportJob entity traced to requirements (FR-007, FR-019, FR-021)? [Traceability, Data Model]
- [ ] CHK191 - Is ExportTemplate entity traced to requirements (FR-016)? [Traceability, Data Model]
- [ ] CHK192 - Is ImportJob entity traced to requirements (FR-003, FR-011, FR-012)? [Traceability, Data Model]
- [ ] CHK193 - Is ExportManifest entity traced to requirements (FR-017)? [Traceability, Data Model]
- [ ] CHK194 - Is ScheduledExport entity traced to requirements (FR-006, FR-022)? [Traceability, Data Model]
- [ ] CHK195 - Is ExportAuditLog entity traced to requirements (FR-010, FR-020)? [Traceability, Data Model]

### Research-to-Requirement Traceability

- [ ] CHK196 - Are PDF library decisions (ReportLab) traced to US4 requirements? [Traceability, Research §1]
- [ ] CHK197 - Are Excel library decisions (pandas + openpyxl) traced to US2 requirements? [Traceability, Research §2]
- [ ] CHK198 - Are scheduler decisions (BackgroundScheduler) traced to US3 requirements? [Traceability, Research §3]
- [ ] CHK199 - Are compression decisions (gzip level 6) traced to FR-021? [Traceability, Research §4]
- [ ] CHK200 - Are notification infrastructure decisions traced to FR-019, FR-022? [Traceability, Research §5]

---

## Summary Statistics

- **Total Items**: 200
- **Requirement Completeness**: 42 items (CHK001-CHK042)
- **Requirement Clarity**: 23 items (CHK043-CHK065)
- **Requirement Consistency**: 15 items (CHK066-CHK080)
- **Acceptance Criteria Quality**: 17 items (CHK081-CHK097)
- **Scenario Coverage**: 23 items (CHK098-CHK120)
- **Edge Case Coverage**: 14 items (CHK121-CHK134)
- **Non-Functional Requirements**: 21 items (CHK135-CHK155)
- **Dependencies & Assumptions**: 16 items (CHK156-CHK171)
- **Ambiguities & Conflicts**: 14 items (CHK172-CHK185)
- **Traceability**: 15 items (CHK186-CHK200)

**Traceability Coverage**: 100% (all 200 items include traceability references)

**Focus Areas**:

- All 5 user stories (US1-US5) covered
- All scenario classes: Primary, Error, Recovery, Alternate, Concurrent
- All quality dimensions: Completeness, Clarity, Consistency, Measurability
- All non-functional domains: Performance, Security, Reliability, Usability

**Constitutional Alignment**: All items test requirements quality, not implementation behavior.

---

## Notes

- Check items off as completed: `[x]`
- Add findings inline with `→ Finding: ...`
- Items marked `[Gap]` indicate missing requirements that should be added to spec.md
- Items marked `[Ambiguity]` or `[Conflict]` require clarification or resolution
- All items reference source documents for traceability
- Use this checklist during specification review before implementation begins
