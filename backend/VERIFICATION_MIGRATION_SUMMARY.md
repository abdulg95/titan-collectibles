# Card Verification Migration Summary

## Overview
Successfully migrated from external ETRNL verification service to in-house Titan NFC verification service.

## Changes Made

### 1. New Verification API (`routes_verification.py`)
- **Endpoint**: `/api/verification/verify`
- **Service**: `https://titan-nfc-144404400823.us-east4.run.app/tags/authenticity`
- **API Key**: `Bearer UIZ3GBlAXrfaHtnAoP4fPPeCjs2mYWAw`
- **Method**: GET
- **Parameters**: `id` (tag id) and `data` (encrypted data)

### 2. Updated Card URL Format
- **Old Format**: External ETRNL URLs
- **New Format**: `https://titansportshq.com/scan?t=000000000002`
- **Template Codes**: 
  - Brady Ellison Regular: `000000000001`
  - Brady Ellison Diamond: `000000000002`
  - Mete Gazoz Regular: `000000000003`
  - Mete Gazoz Diamond: `000000000004`
  - Ella Gibson Regular: `000000000005`
  - Ella Gibson Diamond: `000000000006`
  - Deepika Kumari Regular: `000000000007`
  - Deepika Kumari Diamond: `000000000008`
  - Sara López Regular: `000000000009`
  - Sara López Diamond: `000000000010`
  - Mike Schloesser Regular: `000000000011`
  - Mike Schloesser Diamond: `000000000012`
  - Lim Sihyeon Regular: `000000000013`
  - Lim Sihyeon Diamond: `000000000014`
  - Mathias Fullerton Regular: `000000000015`
  - Mathias Fullerton Diamond: `000000000016`
  - Kim Woojin Regular: `000000000017`
  - Kim Woojin Diamond: `000000000018`

### 3. Updated Frontend (`ScanLanding.tsx`)
- **Backward Compatibility**: Still supports legacy ETRNL URLs
- **New URL Support**: Handles `titansportshq.com/scan?t=000000000002&id=tag123&data=encrypted`
- **Error Handling**: Improved error messages and retry functionality
- **Dual System**: Automatically detects and routes to appropriate verification service

### 4. Database Updates
- **Template Codes**: Added `template_code` field to `CardTemplate` model
- **Migration Script**: `update_card_urls.py` to populate template codes
- **URL Generation**: Templates now include verification URLs in API responses

## API Endpoints

### New Verification Endpoints
- `GET /api/verification/verify` - Main verification endpoint
- `GET /api/verification/verify/<template_code>/<tag_id>` - Verification with template
- `GET /api/verification/scan/<template_code>/<tag_id>` - Legacy compatibility
- `GET /api/verification/dev/templates` - Dev: List all templates with URLs
- `POST /api/verification/dev/fake-verify` - Dev: Simulate verification

### Legacy Endpoints (Still Available)
- `GET /api/scan/resolve` - Original ETRNL verification
- `GET /api/scan/<template>/<tag_id>` - Legacy scan endpoint

## Usage Examples

### New URL Format
```
https://titansportshq.com/scan?t=000000000002&id=abc123&data=encrypted_data_here
```

### API Call Example
```bash
curl "https://titansportshq.com/api/verification/verify?id=abc123&data=encrypted&t=000000000002"
```

## Migration Steps Completed

1. ✅ **Created new verification API** (`routes_verification.py`)
2. ✅ **Registered blueprint** in `app.py`
3. ✅ **Updated frontend** to handle new URL format
4. ✅ **Added backward compatibility** for legacy ETRNL URLs
5. ✅ **Created database update script** (`update_card_urls.py`)
6. ✅ **Added error handling** and improved UX

## Next Steps

1. **Run the database update script** to populate template codes:
   ```bash
   cd backend
   python update_card_urls.py
   ```

2. **Test the verification flow** with real cards

3. **Update any external systems** that generate card URLs to use the new format

4. **Monitor the new verification service** for any issues

## Configuration

### Environment Variables
- `TITAN_NFC_API_KEY`: The Bearer token for the verification service
- `DATABASE_URL`: PostgreSQL connection string

### API Key
The API key is currently hardcoded in the verification route:
```python
TITAN_NFC_KEY = 'Bearer UIZ3GBlAXrfaHtnAoP4fPPeCjs2mYWAw'
```

## Testing

### Development Testing
Use the dev endpoints to test without real cards:
- `GET /api/verification/dev/templates` - List templates with verification URLs
- `POST /api/verification/dev/fake-verify` - Simulate verification

### Production Testing
Test with real card URLs in the new format:
```
https://titansportshq.com/scan?t=000000000002&id=real_tag_id&data=real_encrypted_data
```
