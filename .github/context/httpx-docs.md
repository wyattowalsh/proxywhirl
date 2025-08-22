This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: tools/httpx/**/*.{md,markdown,mdx,rmd,rst,rest,txt,adoc,asciidoc}
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
tools/
  httpx/
    install.mdx
    overview.mdx
    running.mdx
    usage.mdx
```

# Files

## File: tools/httpx/install.mdx
````
---
title: "Installing httpx"
description: "Learn about how to install and get started with httpx"
sidebarTitle: "Install"
---

<Tabs>
  <Tab title="Go">
    <Note> Enter the command below in a terminal to install ProjectDiscovery's httpx using Go. </Note>

    ```bash
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
    ```
  </Tab>
  <Tab title="Brew">
    ```bash
    brew install httpx
    ```

    <Note>Supported in **macOS** (or Linux)</Note>

  </Tab>
  <Tab title="Docker">
    ```bash
    docker pull projectdiscovery/httpx:latest
    ```

    {/* Docker-specific usage instructions can be found [here](./running#running-with-docker). */}

  </Tab>
  <Tab title="GitHub">
   <Note> Enter the commands below in a terminal to install ProjectDiscovery's httpx using GitHub. </Note>
    ```bash
    git clone https://github.com/projectdiscovery/httpx.git; \
    cd httpx/cmd/httpx; \
    go build; \
    mv httpx /usr/local/bin/; \
    httpx -version;
    ```
  </Tab>
  <Tab title="Binary">
    ```bash
    https://github.com/projectdiscovery/httpx/releases
    ```

    <Tip>
    - Download the latest binary for your OS.
    - Unzip the ready to run binary.
    </Tip>

  </Tab>
</Tabs>

## Installation Notes
  - httpx requires the latest version of [**Go**](https://go.dev/doc/install)
  - Add the Go bin path to the system paths. On OSX or Linux, in your terminal use
  
  ```
  echo export PATH=$PATH:$HOME/go/bin >> $HOME/.bashrc
  source $HOME/.bashrc
  ```
  - To add the Go bin path in Windows, [click this link for instructions.](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/)
  - The binary will be located in `$home/go/bin/httpx`
````

## File: tools/httpx/overview.mdx
````
---
title: httpx Overview
description: "An HTTP toolkit that probes services, web servers, and other valuable metadata"
sidebarTitle: Overview
---

## What is **httpx?**

httpx is a fast and multi-purpose HTTP toolkit built to support running multiple probes using a public library. 
Probes are specific tests or checks to gather information about web servers, URLs, or other HTTP elements. 
Httpx is designed to maintain result reliability with an increased number of threads.

Typically, users employ httpx to efficiently identify and analyze web server configurations, verify HTTP responses, and diagnose potential vulnerabilities or misconfigurations. 
It can also be in a pipeline that transitions from asset identification to technology enrichment and then feeds into detection of vulnerabilities.

## Features and capabilities

- A simple and modular code base for easy contribution 
- Configurable flags to probe multiple elements
- Support for multiple HTTP based probes
- Smart auto-fallback from https to http 
- Support for  hosts, URLs and CIDR 
- Handling for edge cases: retries, backoffs for WAFs
- UI Dashboard for results


## Additional httpx resources

As an open source tool with a robust community there are a lot of community-created resources available. 
We are happy to share those to offer even more information about our tools. 
<i>ProjectDiscovery’s httpx should not be confused with the httpx python library.</i>

<Note>Sharing these resources **is not formal approval or a recommendation** from ProjectDiscovery. 
We cannot provide an endorsement of accuracy or validation that content is up-to-date. Anything shared here should be approached with caution.</Note> 

- https://www.kali.org/tools/httpx-toolkit/
- https://www.hackingarticles.in/a-detailed-guide-on-httpx/

## Support 
Questions about using httpx? Issues working through installation? Cool story or use case you want to share? Get in touch! 

Check out the [Help](/help) section of the docs or reach out to us on [Discord](https://discord.com/invite/projectdiscovery).
````

## File: tools/httpx/running.mdx
````
---
title: 'Running httpx'
description: "Learn about running httpx with examples including commands and output"
sidebarTitle: 'Running'
---

For all of the flags and options available for `httpx` be sure to check out the [Usage](/tools/httpx/usage) page. On this page we'll share examples running httpx with specific flags and goals
and the output you can expect from each. 

<Note> If you have questions, reach out to us through [Help](/help). </Note>

## Basic Examples

### ASN Fingerprint
Use `httpx` with the `-asn` flag for ASN (Autonomous System Number) fingerprinting, an effective technique for mapping the network affiliations of various domains. 

```
subfinder -d hackerone.com -silent | httpx -asn
    __    __  __       _  __
   / /_  / /_/ /_____ | |/ /
  / __ \/ __/ __/ __ \|   /
 / / / / /_/ /_/ /_/ /   |
/_/ /_/\__/\__/ .___/_/|_|
             /_/              v1.2.1

      projectdiscovery.io

Use with caution. You are responsible for your actions.
Developers assume no liability and are not responsible for any misuse or damage.
https://mta-sts.managed.hackerone.com [AS54113, FASTLY, US]
https://gslink.hackerone.com [AS16509, AMAZON-02, US]
https://www.hackerone.com [AS13335, CLOUDFLARENET, US]
https://mta-sts.forwarding.hackerone.com [AS54113, FASTLY, US]
https://resources.hackerone.com [AS16509, AMAZON-02, US]
https://support.hackerone.com [AS13335, CLOUDFLARENET, US]
https://mta-sts.hackerone.com [AS54113, FASTLY, US]
https://docs.hackerone.com [AS54113, FASTLY, US]
https://api.hackerone.com [AS13335, CLOUDFLARENET, US]
```

### ASN Input 
Specify an [autonomous system's number (ASN)](https://en.wikipedia.org/wiki/Autonomous_system_(Internet)) and `httpx` will fetch all ip addresses of that autonomous system and probe them

```
echo AS14421 | httpx -silent

https://216.101.17.248
https://216.101.17.249
https://216.101.17.250
https://216.101.17.251
https://216.101.17.252
```

### CIDR Input 
Run `httpx` with CIDR input (for example 173.0.84.0/24)

```
echo 173.0.84.0/24 | httpx -silent

https://173.0.84.29
https://173.0.84.43
https://173.0.84.31
https://173.0.84.44
https://173.0.84.12
https://173.0.84.4
https://173.0.84.36
https://173.0.84.45
https://173.0.84.14
https://173.0.84.25
https://173.0.84.46
https://173.0.84.24
https://173.0.84.32
https://173.0.84.9
https://173.0.84.13
https://173.0.84.6
https://173.0.84.16
https://173.0.84.34
```
### Docker Run
Use Docker to run `httpx` in an isolated container. For example, by piping subdomain lists into the Docker container, you can seamlessly perform probing across multiple targets, harnessing the power of `httpx` without direct installation requirements.

```
cat sub_domains.txt | docker run -i projectdiscovery/httpx

    __    __  __       _  __
   / /_  / /_/ /_____ | |/ /
  / __ \/ __/ __/ __ \|   /
 / / / / /_/ /_/ /_/ /   |
/_/ /_/\__/\__/ .___/_/|_|
             /_/              v1.1.2

      projectdiscovery.io

Use with caution. You are responsible for your actions
Developers assume no liability and are not responsible for any misuse or damage.
https://mta-sts.forwarding.hackerone.com
https://mta-sts.hackerone.com
https://mta-sts.managed.hackerone.com
https://www.hackerone.com
https://api.hackerone.com
https://gslink.hackerone.com
https://resources.hackerone.com
https://docs.hackerone.com
https://support.hackerone.com
```
### Error Page Classifier and Filtering
The Error Page Classifier and Filtering feature aims to add intelligence to `httpx` by enabling `httpx` to classify and filter out common error pages returned by web applications. 
It is an enhancement geared towards reducing noise and helping focus on actual results. 

Using the `-fep` or `-filter-error-page` option creates a filtered error page in the file `filtered_error_page.json` in jsonline format.

```
httpx -l urls.txt -path /v1/api -fep

    __    __  __       _  __
   / /_  / /_/ /_____ | |/ /
  / __ \/ __/ __/ __ \|   /
 / / / / /_/ /_/ /_/ /   |
/_/ /_/\__/\__/ .___/_/|_|
             /_/

                projectdiscovery.io

[INF] Current httpx version v1.3.3 (latest)
https://scanme.sh/v1/api
```
### Favicon Hash
Extract and display the mmh3 hash of the '/favicon.ico' file from given targets.

```
subfinder -d hackerone.com -silent | httpx -favicon

    __    __  __       _  __
   / /_  / /_/ /_____ | |/ /
  / __ \/ __/ __/ __ \|   /
 / / / / /_/ /_/ /_/ /   |
/_/ /_/\__/\__/ .___/_/|_|
             /_/              v1.1.5

      projectdiscovery.io

Use with caution. You are responsible for your actions.
Developers assume no liability and are not responsible for any misuse or damage.
https://docs.hackerone.com/favicon.ico [595148549]
https://hackerone.com/favicon.ico [595148549]
https://mta-sts.managed.hackerone.com/favicon.ico [-1700323260]
https://mta-sts.forwarding.hackerone.com/favicon.ico [-1700323260]
https://support.hackerone.com/favicon.ico [-1279294674]
https://gslink.hackerone.com/favicon.ico [1506877856]
https://resources.hackerone.com/favicon.ico [-1840324437]
https://api.hackerone.com/favicon.ico [566218143]
https://mta-sts.hackerone.com/favicon.ico [-1700323260]
https://www.hackerone.com/favicon.ico [778073381]
```
### File/Path Bruteforce
Use `httpx` with the `-path` option for efficient File/Path Bruteforcing. This feature allows probing specific paths across multiple URLs, uncovering response codes and revealing potentially vulnerable or unsecured endpoints in web applications.

```
httpx -l urls.txt -path /v1/api -sc

    __    __  __       _  __
   / /_  / /_/ /_____ | |/ /
  / __ \/ __/ __/ __ \|   /
 / / / / /_/ /_/ /_/ /   |
/_/ /_/\__/\__/ .___/_/|_|
             /_/              v1.1.5

      projectdiscovery.io

Use with caution. You are responsible for your actions.
Developers assume no liability and are not responsible for any misuse or damage.
https://mta-sts.managed.hackerone.com/v1/api [404]
https://mta-sts.hackerone.com/v1/api [404]
https://mta-sts.forwarding.hackerone.com/v1/api [404]
https://docs.hackerone.com/v1/api [404]
https://api.hackerone.com/v1/api [401]
https://hackerone.com/v1/api [302]
https://support.hackerone.com/v1/api [404]
https://resources.hackerone.com/v1/api [301]
https://gslink.hackerone.com/v1/api [404]
http://www.hackerone.com/v1/api [301]
```

### File Input
Run `httpx` with the `-probe` flag against all the hosts in hosts.txt to return URLs with probed status.

```
httpx -list hosts.txt -silent -probe

http://ns.hackerone.com [FAILED]
https://docs.hackerone.com [SUCCESS]
https://mta-sts.hackerone.com [SUCCESS]
https://mta-sts.managed.hackerone.com [SUCCESS]
http://email.hackerone.com [FAILED]
https://mta-sts.forwarding.hackerone.com [SUCCESS]
http://links.hackerone.com [FAILED]
https://api.hackerone.com [SUCCESS]
https://www.hackerone.com [SUCCESS]
http://events.hackerone.com [FAILED]
https://support.hackerone.com [SUCCESS]
https://gslink.hackerone.com [SUCCESS]
http://o1.email.hackerone.com [FAILED]
http://info.hackerone.com [FAILED]
https://resources.hackerone.com [SUCCESS]
http://o2.email.hackerone.com [FAILED]
http://o3.email.hackerone.com [FAILED]
http://go.hackerone.com [FAILED]
http://a.ns.hackerone.com [FAILED]
http://b.ns.hackerone.com [FAILED]
```
### JARM Fingerprint
Use `httpx` with the `-jarm` flag to leverage JARM fingerprinting, a specialized tool for active TLS server fingerprinting. 
This approach enables the identification and categorization of servers based on their TLS configurations, making it an effective method for detecting and analyzing diverse internet servers, 
including potential security threats.

```
subfinder -d hackerone.com -silent | httpx -jarm
    __    __  __       _  __
   / /_  / /_/ /_____ | |/ /
  / __ \/ __/ __/ __ \|   /
 / / / / /_/ /_/ /_/ /   |
/_/ /_/\__/\__/ .___/_/|_|
             /_/              v1.2.1

      projectdiscovery.io

Use with caution. You are responsible for your actions.
Developers assume no liability and are not responsible for any misuse or damage.
https://www.hackerone.com [29d3dd00029d29d00042d43d00041d5de67cc9954cc85372523050f20b5007]
https://mta-sts.hackerone.com [29d29d00029d29d00042d43d00041d2aa5ce6a70de7ba95aef77a77b00a0af]
https://mta-sts.managed.hackerone.com [29d29d00029d29d00042d43d00041d2aa5ce6a70de7ba95aef77a77b00a0af]
https://docs.hackerone.com [29d29d00029d29d00042d43d00041d2aa5ce6a70de7ba95aef77a77b00a0af]
https://support.hackerone.com [29d3dd00029d29d00029d3dd29d29d5a74e95248e58a6162e37847a24849f7]
https://api.hackerone.com [29d3dd00029d29d00042d43d00041d5de67cc9954cc85372523050f20b5007]
https://mta-sts.forwarding.hackerone.com [29d29d00029d29d00042d43d00041d2aa5ce6a70de7ba95aef77a77b00a0af]
https://resources.hackerone.com [2ad2ad0002ad2ad0002ad2ad2ad2ad043bfbd87c13813505a1b60adf4f6ff5]
```
### Tool Chain 
Combining `httpx` with other tools like `subfinder` can elevate your web reconnaissance. 
For example, pipe results from `subfinder` directly into 'httpx' to efficiently identify active web servers and their technologies across various subdomains of a given target.

```
subfinder -d hackerone.com -silent| httpx -title -tech-detect -status-code

    __    __  __       _  __
   / /_  / /_/ /_____ | |/ /
  / __ \/ __/ __/ __ \|   /
 / / / / /_/ /_/ /_/ /   |
/_/ /_/\__/\__/ .___/_/|_|
             /_/              v1.1.1

    projectdiscovery.io

Use with caution. You are responsible for your actions
Developers assume no liability and are not responsible for any misuse or damage.
https://mta-sts.managed.hackerone.com [404] [Page not found · GitHub Pages] [Varnish,GitHub Pages,Ruby on Rails]
https://mta-sts.hackerone.com [404] [Page not found · GitHub Pages] [Varnish,GitHub Pages,Ruby on Rails]
https://mta-sts.forwarding.hackerone.com [404] [Page not found · GitHub Pages] [GitHub Pages,Ruby on Rails,Varnish]
https://docs.hackerone.com [200] [HackerOne Platform Documentation] [Ruby on Rails,jsDelivr,Gatsby,React,webpack,Varnish,GitHub Pages]
https://support.hackerone.com [301,302,301,200] [HackerOne] [Cloudflare,Ruby on Rails,Ruby]
https://resources.hackerone.com [301,301,404] [Sorry, no Folders found.]
```

### URL probe
Run `httpx` against all the hosts and subdomains in hosts.txt to return URLs running an HTTP webserver.

```
cat hosts.txt | httpx 

    __    __  __       _  __
   / /_  / /_/ /_____ | |/ /
  / __ \/ __/ __/ __ \|   / 
 / / / / /_/ /_/ /_/ /   |  
/_/ /_/\__/\__/ .___/_/|_|   v1.1.1  
             /_/            

    projectdiscovery.io

[WRN] Use with caution. You are responsible for your actions
[WRN] Developers assume no liability and are not responsible for any misuse or damage.

https://mta-sts.managed.hackerone.com
https://mta-sts.hackerone.com
https://mta-sts.forwarding.hackerone.com
https://docs.hackerone.com
https://www.hackerone.com
https://resources.hackerone.com
https://api.hackerone.com
https://support.hackerone.com
```

## UI Dashboard (PDCP Integration)

#### Configure API Key

To upload your assets to PDCP you will need to create a free API Key 

- **Obtain API Key:**

  - Visit https://cloud.projectdiscovery.io 
  - Open the setting menu from the top right and select "API Key" to create your API Key
    <img class="block" src="/images/pdcp-api-key.png" alt="PDCP API Key" />
  - Use the `httpx -auth` command, and enter your API key when prompted.

#### Configure Team (Optional)

If you want to upload the asset results to a team workspace instead of your personal workspace, you can configure the Team ID. You can use either the CLI option or the environment variable, depending on your preference.

- **Obtain Team ID:**
  - To obtain your Team ID, navigate to [https://cloud.projectdiscovery.io/settings/team](https://cloud.projectdiscovery.io/settings/team) and copy the Team ID from the top right section.

  ![image](https://github.com/user-attachments/assets/76a9f102-1626-4c87-8d9e-37c30417f19e)


- **CLI Option:**
  - Use the `-tid` or `-team-id` option to specify the team ID.
  - Example: `nuclei -tid XXXXXX -dashboard`

- **ENV Variable:**
  - Set the `PDCP_TEAM_ID` environment variable to your team ID.
  - Example: `export PDCP_TEAM_ID=XXXXX`

Either of these options is sufficient to configure the Team ID.

#### Run httpx with UI Dashboard

To run `httpx` and upload the results to the UI Dashboard:

```console
$ chaos -d hackerone.com | httpx -dashboard

    __    __  __       _  __
   / /_  / /_/ /_____ | |/ /
  / __ \/ __/ __/ __ \|   /
 / / / / /_/ /_/ /_/ /   |
/_/ /_/\__/\__/ .___/_/|_|
             /_/

        projectdiscovery.io

[INF] Current httpx version v1.6.6 (latest)
[INF] To view results on UI dashboard, visit https://cloud.projectdiscovery.io/assets upon completion.
http://a.ns.hackerone.com
https://www.hackerone.com
http://b.ns.hackerone.com
https://api.hackerone.com
https://mta-sts.forwarding.hackerone.com
https://docs.hackerone.com
https://support.hackerone.com
https://mta-sts.hackerone.com
https://gslink.hackerone.com
[INF] Found 10 results, View found results in dashboard : https://cloud.projectdiscovery.io/assets/cqd56lebh6us73bi22pg
```

![image](https://blog.projectdiscovery.io/content/images/size/w1600/2024/08/image.png)

#### Uploading to an Existing Asset Group

To upload new assets to an existing asset group:

```console
$ chaos -d hackerone.com | httpx -dashboard -aid existing-asset-id
```

#### Setting an Asset Group Name

To set a custom asset group name:

```console
$ chaos -d hackerone.com | httpx -dashboard -aname "Custom Asset Group"
```

### Additional upload options

- `-pd, -dashboard`: Enable uploading of `httpx` results to the ProjectDiscovery Cloud (PDCP) UI Dashboard.
- `-aid, -asset-id string`: Upload new assets to an existing asset ID (optional).
- `-aname, -asset-name string`: Set the asset group name (optional).
- `-pdu, -dashboard-upload string`: Upload `httpx` output file (jsonl) to the ProjectDiscovery Cloud (PDCP) UI Dashboard.

### Environment Variables

- `export ENABLE_CLOUD_UPLOAD=true`: Enable dashboard upload by default.
- `export DISABLE_CLOUD_UPLOAD_WARN=true`: Disable dashboard warning.
- `export PDCP_TEAM_ID=XXXXX`: Set the team ID for the ProjectDiscovery Cloud Platform.

## Expanded Examples

### Using httpx as a library

httpx can be used as a library by creating an instance of the Option struct and populating it with the same options that would be specified via CLI. 
Once validated, the struct should be passed to a runner instance (to be closed at the end of the program) and the RunEnumeration method should be called. 
- A basic example of how to use httpx as a library is available in the [GitHub examples](https://github.com/projectdiscovery/httpx/tree/main/examples) folder. 

### Using httpx screenshot

Httpx includes support for taking a screenshot with `-screenshot` that gives users the ability to take screenshots of target URLs, pages, or endpoints along with the rendered DOM. 
This functionality enables a comprehensive view of the target's visual content.

Rendered DOM body is also included in json line output when `-screenshot` option is used with `-json` option.

To use this feature, add the `-screenshot` flag to the `httpx` command. 

`httpx -screenshot -u https://example.com`

<Tip> Screenshots are captured using a headless browser, and as a result `httpx` will be slower when using the `-screenshot` option.</Tip>

#### Domain, Subdomain, and Path Support
The `-screenshot` option is versatile and can be used to capture screenshots for domains, subdomains, and even specific paths when used in conjunction with the `-path` option:

```
httpx -screenshot -u example.com
httpx -screenshot -u https://example.com/login
httpx -screenshot -path fuzz_path.txt -u https://example.com
```

#### Using with Other Tools

In the example below we're providing subfinder output to the `httpx` screenshot.

```
subfinder -d example.com | httpx -screenshot
```

#### System Chrome Support
By default, `httpx` uses the go-rod library to install and manage Chrome for taking screenshots. 
However, if you prefer to use your locally installed system Chrome, add the `-system-chrome` flag:

```
httpx -screenshot -system-chrome -u https://example.com
```

#### Output Directory
Screenshots are stored in the output/screenshot directory by default. To specify a custom output directory, use the `-srd` option:

```
httpx -screenshot -srd /path/to/custom/directory -u https://example.com
```

#### Body Preview
Body preview shows first N characters of response. And strip html tags in response.

```
httpx -u https://example.com -silent -body-preview
https://example.com [Example Domain This domain is for use in illustrative examples in documents. You may use this domai]
```
```
httpx -u https://example.com -silent -body-preview=200 -strip=html
https://example.com [Example Domain This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission. More information...]
```
````

## File: tools/httpx/usage.mdx
````
---
title: "Httpx Usage"
description: "Learn httpx usage including flags, probes, and options"
sidebarTitle: "Usage"
---
## Access help 

Use `httpx - h` to display all help options. 

## Httpx help options
```
Flags:
INPUT:
   -l, -list string      input file containing list of hosts to process
   -rr, -request string  file containing raw request
   -u, -target string[]  input target host(s) to probe

PROBES:
   -sc, -status-code     display response status-code
   -cl, -content-length  display response content-length
   -ct, -content-type    display response content-type
   -location             display response redirect location
   -favicon              display mmh3 hash for '/favicon.ico' file
   -hash string          display response body hash (supported: md5,mmh3,simhash,sha1,sha256,sha512)
   -jarm                 display jarm fingerprint hash
   -rt, -response-time   display response time
   -lc, -line-count      display response body line count
   -wc, -word-count      display response body word count
   -title                display page title
   -bp, -body-preview    display first N characters of response body (default 100)
   -server, -web-server  display server name
   -td, -tech-detect     display technology in use based on wappalyzer dataset
   -method               display http request method
   -websocket            display server using websocket
   -ip                   display host ip
   -cname                display host cname
   -asn                  display host asn information
   -cdn                  display cdn/waf in use
   -probe                display probe status

HEADLESS:
   -ss, -screenshot                 enable saving screenshot of the page using headless browser
   -system-chrome                   enable using local installed chrome for screenshot
   -esb, -exclude-screenshot-bytes  enable excluding screenshot bytes from json output
   -ehb, -exclude-headless-body     enable excluding headless header from json output

MATCHERS:
   -mc, -match-code string            match response with specified status code (-mc 200,302)
   -ml, -match-length string          match response with specified content length (-ml 100,102)
   -mlc, -match-line-count string     match response body with specified line count (-mlc 423,532)
   -mwc, -match-word-count string     match response body with specified word count (-mwc 43,55)
   -mfc, -match-favicon string[]      match response with specified favicon hash (-mfc 1494302000)
   -ms, -match-string string          match response with specified string (-ms admin)
   -mr, -match-regex string           match response with specified regex (-mr admin)
   -mcdn, -match-cdn string[]         match host with specified cdn provider (cloudfront, fastly, google, leaseweb, stackpath)
   -mrt, -match-response-time string  match response with specified response time in seconds (-mrt '< 1')
   -mdc, -match-condition string      match response with dsl expression condition

EXTRACTOR:
   -er, -extract-regex string[]   display response content with matched regex
   -ep, -extract-preset string[]  display response content matched by a pre-defined regex (ipv4,mail,url)

FILTERS:
   -fc, -filter-code string            filter response with specified status code (-fc 403,401)
   -fep, -filter-error-page            filter response with ML based error page detection
   -fd, -filter-duplicates             filter out near-duplicate responses (only first response is retained)
   -fl, -filter-length string          filter response with specified content length (-fl 23,33)
   -flc, -filter-line-count string     filter response body with specified line count (-flc 423,532)
   -fwc, -filter-word-count string     filter response body with specified word count (-fwc 423,532)
   -ffc, -filter-favicon string[]      filter response with specified favicon hash (-ffc 1494302000)
   -fs, -filter-string string          filter response with specified string (-fs admin)
   -fe, -filter-regex string           filter response with specified regex (-fe admin)
   -fcdn, -filter-cdn string[]         filter host with specified cdn provider (cloudfront, fastly, google, leaseweb, stackpath)
   -frt, -filter-response-time string  filter response with specified response time in seconds (-frt '> 1')
   -fdc, -filter-condition string      filter response with dsl expression condition
   -strip                              strips all tags in response. supported formats: html,xml (default html)

RATE-LIMIT:
   -t, -threads int              number of threads to use (default 50)
   -rl, -rate-limit int          maximum requests to send per second (default 150)
   -rlm, -rate-limit-minute int  maximum number of requests to send per minute

MISCELLANEOUS:
   -pa, -probe-all-ips        probe all the ips associated with same host
   -p, -ports string[]        ports to probe (nmap syntax: eg http:1,2-10,11,https:80)
   -path string               path or list of paths to probe (comma-separated, file)
   -tls-probe                 send http probes on the extracted TLS domains (dns_name)
   -csp-probe                 send http probes on the extracted CSP domains
   -tls-grab                  perform TLS(SSL) data grabbing
   -pipeline                  probe and display server supporting HTTP1.1 pipeline
   -http2                     probe and display server supporting HTTP2
   -vhost                     probe and display server supporting VHOST
   -ldv, -list-dsl-variables  list json output field keys name that support dsl matcher/filter

UPDATE:
   -up, -update                 update httpx to latest version
   -duc, -disable-update-check  disable automatic httpx update check

OUTPUT:
   -o, -output string                  file to write output results
   -oa, -output-all                    filename to write output results in all formats
   -sr, -store-response                store http response to output directory
   -srd, -store-response-dir string    store http response to custom directory
   -csv                                store output in csv format
   -csvo, -csv-output-encoding string  define output encoding
   -j, -json                           store output in JSONL(ines) format
   -irh, -include-response-header      include http response (headers) in JSON output (-json only)
   -irr, -include-response             include http request/response (headers + body) in JSON output (-json only)
   -irrb, -include-response-base64     include base64 encoded http request/response in JSON output (-json only)
   -include-chain                      include redirect http chain in JSON output (-json only)
   -store-chain                        include http redirect chain in responses (-sr only)
   -svrc, -store-vision-recon-cluster  include visual recon clusters (-ss and -sr only)

CONFIGURATIONS:
   -config string                path to the httpx configuration file (default $HOME/.config/httpx/config.yaml)
   -r, -resolvers string[]       list of custom resolver (file or comma separated)
   -allow string[]               allowed list of IP/CIDR's to process (file or comma separated)
   -deny string[]                denied list of IP/CIDR's to process (file or comma separated)
   -sni, -sni-name string        custom TLS SNI name
   -random-agent                 enable Random User-Agent to use (default true)
   -H, -header string[]          custom http headers to send with request
   -http-proxy, -proxy string    http proxy to use (eg http://127.0.0.1:8080)
   -unsafe                       send raw requests skipping golang normalization
   -resume                       resume scan using resume.cfg
   -fr, -follow-redirects        follow http redirects
   -maxr, -max-redirects int     max number of redirects to follow per host (default 10)
   -fhr, -follow-host-redirects  follow redirects on the same host
   -rhsts, -respect-hsts         respect HSTS response headers for redirect requests
   -vhost-input                  get a list of vhosts as input
   -x string                     request methods to probe, use 'all' to probe all HTTP methods
   -body string                  post body to include in http request
   -s, -stream                   stream mode - start elaborating input targets without sorting
   -sd, -skip-dedupe             disable dedupe input items (only used with stream mode)
   -ldp, -leave-default-ports    leave default http/https ports in host header (eg. http://host:80 - https://host:443
   -ztls                         use ztls library with autofallback to standard one for tls13
   -no-decode                    avoid decoding body
   -tlsi, -tls-impersonate       enable experimental client hello (ja3) tls randomization
   -no-stdin                     Disable Stdin processing

DEBUG:
   -health-check, -hc        run diagnostic check up
   -debug                    display request/response content in cli
   -debug-req                display request content in cli
   -debug-resp               display response content in cli
   -version                  display httpx version
   -stats                    display scan statistic
   -profile-mem string       optional httpx memory profile dump file
   -silent                   silent mode
   -v, -verbose              verbose mode
   -si, -stats-interval int  number of seconds to wait between showing a statistics update (default: 5)
   -nc, -no-color            disable colors in cli output

OPTIMIZATIONS:
   -nf, -no-fallback                  display both probed protocol (HTTPS and HTTP)
   -nfs, -no-fallback-scheme          probe with protocol scheme specified in input 
   -maxhr, -max-host-error int        max error count per host before skipping remaining path/s (default 30)
   -ec, -exclude-cdn                  skip full port scans for CDN/WAF (only checks for 80,443)
   -retries int                       number of retries
   -timeout int                       timeout in seconds (default 10)
   -delay value                       duration between each http request (eg: 200ms, 1s) (default -1ns)
   -rsts, -response-size-to-save int  max response size to save in bytes (default 2147483647)
   -rstr, -response-size-to-read int  max response size to read in bytes (default 2147483647)
   ```

## Notes on usage

- As default an `httpx` probe with an HTTPS scheme will fall-back to HTTP only if HTTPS is not reachable.
- The `-no-fallback` flag can be used to probe and display both HTTP and HTTPS result.
- Custom scheme for ports can be defined, for example `-ports http:443,http:80,https:8443`
- Custom resolver supports multiple protocol (doh|tcp|udp) in form of protocol:resolver:port (for example `udp:127.0.0.1:53`)
- The following flags should be used for specific use cases instead of running them as default with other probes:
  - `- ports`
  -  `- path`
  - `- vhost`
  - `- screenshot`
  - `- csp-probe`
  - `- tls-probe`
  - `- favicon`
  - `- http2`
  - `- pipeline`
  - `- tls-impersonate`
````
