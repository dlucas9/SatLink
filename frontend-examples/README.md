# Frontend Examples

This directory contains example implementations for integrating with the SatLink REST API.

## Files

- **`satlink-api-client.js`** - JavaScript client library for SatLink API
- **`demo.html`** - Complete HTML demo application with interactive forms
- **`README.md`** - This file

## Quick Start

1. **Start the SatLink API server:**
   ```bash
   cd /home/dlucas/src/SatLink
   python satlink_api.py
   ```

2. **Open the demo in a web browser:**
   ```bash
   # Open demo.html in your browser
   firefox demo.html
   # or
   google-chrome demo.html
   ```

3. **Or serve it via a local web server:**
   ```bash
   # Python 3
   python -m http.server 8080
   
   # Then visit: http://localhost:8080/demo.html
   ```

## API Client Usage

### Basic Example
```javascript
// Import the client
const api = new SatLinkAPI('http://localhost:5000');

// Single point calculation
const params = {
  sat_long: -70,
  freq: 12,
  eirp: 54,
  b_transponder: 36,
  b_util: 9,
  mod: "8PSK",
  fec: "120/180",
  site_lat: -3.7,
  site_long: -45.9
};

try {
  const result = await api.calculateSinglePoint(params);
  console.log('Availability:', result.results.availability.percentage + '%');
} catch (error) {
  console.error('Error:', error.message);
}
```

### Validation
```javascript
// Validate parameters before sending
const errors = validateSinglePointParams(params);
if (errors.length > 0) {
  console.error('Validation errors:', errors);
  return;
}
```

### Result Formatting
```javascript
// Format results for display
const formatted = formatResults(result.results);
console.log(formatted.availability); // "99.95%"
console.log(formatted.link_margin);  // "12.5 dB"
```

## Demo Features

The HTML demo (`demo.html`) includes:

- **Three interactive tabs:**
  - Single Point calculation
  - Multi-Point analysis
  - Antenna Sizing analysis

- **Form validation** with real-time feedback
- **Error handling** with user-friendly messages
- **Loading indicators** during calculations
- **Formatted results** with color-coded status indicators
- **Responsive design** that works on desktop and mobile

## Integration Tips

1. **CORS**: The API includes CORS headers, so you can call it from any domain
2. **Error Handling**: Always wrap API calls in try-catch blocks
3. **Validation**: Validate inputs client-side before sending to API
4. **Loading States**: Show loading indicators for better UX
5. **Result Formatting**: Use the provided formatting functions for consistent display

## Customization

You can customize the demo for your needs:

- **Styling**: Modify the CSS in `demo.html`
- **Forms**: Add/remove form fields as needed
- **Validation**: Extend the validation functions
- **Results**: Customize the result display format
- **Charts**: Add charting libraries for visual data representation

## Production Considerations

For production use, consider:

- **Authentication**: Add API key authentication if needed
- **Rate Limiting**: Implement client-side rate limiting
- **Caching**: Cache results for repeated calculations
- **Error Logging**: Log errors for debugging
- **Performance**: Debounce form inputs for real-time calculations

## Browser Compatibility

The examples use modern JavaScript features and should work in:
- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

For older browsers, consider using a transpiler like Babel.

## Support

For help with frontend integration:
1. Check the [Frontend API Manual](../FRONTEND_API_MANUAL.md)
2. Review the [API Usage Guide](../API_USAGE.md)
3. Contact: christianfragoas@gmail.com
