# Development Tools

## Fake Tag Scanning (Local Development)

For local development, you can simulate ETRNL tag scans without needing physical NFC tags or calling the external ETRNL API.

### How to Use

1. **Make sure you have templates created**
   - Go to `/admin/templates` and create at least one card template
   - Or seed templates using your seed scripts

2. **Access the Dev Scan page**
   - Navigate to: `http://localhost:5173/dev/scan`
   - You'll see a list of all available templates

3. **Simulate a tag scan**
   - Click the "📱 Scan Tag" button next to any template
   - This will:
     - Generate a random tag UID and tag ID (using `secrets.token_hex()`)
     - Mint a new card instance
     - Save it to the database with the fake tag data
     - Increment the template's minted count
     - Redirect you through the same flow as a real scan

4. **Test the full flow**
   - **First scan**: You'll see the "Card has been registered" message
   - **View card**: Navigate to the card view and see the card image
   - **Add to collection**: Click the floating + button to claim the card
   - **Subsequent scans**: Scanning again would show the card as already registered

### API Endpoint

**POST** `/api/scan/dev/fake-scan`

**Request Body:**
```json
{
  "template_id": "uuid-of-template",
  "force_new": true
}
```

**Response:**
```json
{
  "ok": true,
  "state": "unclaimed",
  "cardId": "uuid-of-card-instance",
  "minted": true,
  "dev_mode": true,
  "fake_uid": "a1b2c3d4e5f60708",
  "fake_tag_id": "fake-9a8b7c6d5e4f",
  "serial_no": 1
}
```

### Security

- This endpoint is **dev-only** and will return 403 if `FLASK_ENV=production`
- The endpoint generates cryptographically random tag IDs using Python's `secrets` module
- Each scan creates a unique card instance in the database

### Testing Different Scenarios

**Test re-scanning the same card:**
```bash
curl -X POST http://localhost:5001/api/scan/dev/fake-scan \
  -H "Content-Type: application/json" \
  -d '{"template_id": "your-template-id", "force_new": false}'
```

This will try to find an existing card with the same fake UID (useful for testing the re-scan flow).

### Database

All fake scans create real database entries:
- New `CardInstance` records with random `etrnl_tag_uid` and `etrnl_tag_id`
- `ScanEvent` records for audit trail
- Incremented `minted_count` on the template

You can view these in your database or through the admin panel.

