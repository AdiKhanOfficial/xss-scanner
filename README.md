
# XSS Scanner by Adil Khan

A powerful, Python-based Cross-Site Scripting (XSS) vulnerability scanner built for ethical hacking and security testing. This tool crawls websites to identify and test links and forms for potential XSS vulnerabilities.

## Features

- **Site Crawling**: Crawl and fetch internal and external links from a target website.
- **Form-Based XSS Testing**: Detect XSS vulnerabilities in forms by injecting payloads.
- **URL-Based XSS Testing**: Identify XSS vulnerabilities in URL parameters.
- **Customizable Payloads**: Add or modify payloads for testing.
- **Debugging Support**: Optional verbose mode for detailed logs.
- **Excluded URLs**: Define a list of URLs to skip during scanning.
- **Cookie Support**: Use cookies for authenticated sessions.

## How It Works

1. **Crawling**: The tool discovers links on the target website, including internal, external, and fuzzable links (URLs with parameters).
2. **Testing Forms**: Submits payloads to detected forms to identify vulnerabilities.
3. **Testing URLs**: Injects payloads into URL parameters to identify vulnerabilities.
4. **Results**: Reports all vulnerable links with the associated payloads.

## Requirements

- Python 3.9 or above
- Required Python packages (install via `requirements.txt`)

### Required Libraries

- `colorama` (for colored output)
- `validators` (for URL validation)
- `beautifulsoup4` (for parsing HTML content)
- `requests` (for HTTP requests)
- `lxml` (for XML parsing)
- `regex` (for advanced regex matching)
- `art` (for ASCII art banners)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AdiKhanOfficial/xss-scanner.git
   cd xss-scanner
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python xss_scanner.py
   ```

## Usage

1. **Input URL**: Provide the target URL for scanning.
2. **Options**: Choose whether to crawl the site or directly test forms and URLs.
3. **View Results**: Get a detailed report of vulnerable links and payloads.

### Settings

- **`settings.xml`**: Configure cookies and excluded URLs for advanced usage.

Example `settings.xml`:
```xml
<settings>
    <cookies>
        <cookie name="sessionid" value="your_session_id_here"/>
    </cookies>
    <exluded>
        <exclude value=".jpg"/>
        <exclude value=".png"/>
    </exluded>
</settings>
```

## Example Run

```bash
Enter URL: https://example.com
[*] Crawling started...
[*] Internal links found: 10
[*] Testing forms for XSS vulnerabilities...
[*] Vulnerable link found: https://example.com/vuln_page
[*] Payload: <script>alert('XSS Scanner')</script>
```

## Legal Disclaimer

This tool is intended for educational purposes and authorized penetration testing only. **Unauthorized use of this tool on a website without permission is illegal and punishable by law.** The author is not responsible for any misuse of this software.

---

**Developed by Adil Khan | [AdiKhanOfficial](https://github.com/AdiKhanOfficial)**  
For contributions or issues, feel free to open a pull request or an issue.

## Contact
For further queries or assistance, contact:

**Adil Khan**  
- [Website](https://adikhanofficial.com)  
- [GitHub](https://github.com/AdiKhanOfficial)  
- [WhatsApp](https://wa.me/+923065305216)  
