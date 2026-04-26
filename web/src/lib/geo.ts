/**
 * Geographic utilities and constants for proxy visualization
 */

// Country code to flag emoji
export function getFlag(countryCode: string): string {
  if (!countryCode || countryCode.length !== 2 || countryCode === "Unknown") return "🌐"
  const codePoints = countryCode
    .toUpperCase()
    .split("")
    .map((char) => 127397 + char.charCodeAt(0))
  return String.fromCodePoint(...codePoints)
}

// Country code to name mapping
export const COUNTRY_NAMES: Record<string, string> = {
  US: "United States",
  CN: "China",
  RU: "Russia",
  BR: "Brazil",
  IN: "India",
  DE: "Germany",
  FR: "France",
  GB: "United Kingdom",
  ID: "Indonesia",
  JP: "Japan",
  KR: "South Korea",
  VN: "Vietnam",
  TH: "Thailand",
  PH: "Philippines",
  SG: "Singapore",
  MY: "Malaysia",
  CA: "Canada",
  AU: "Australia",
  NL: "Netherlands",
  UA: "Ukraine",
  PL: "Poland",
  TR: "Turkey",
  IT: "Italy",
  ES: "Spain",
  MX: "Mexico",
  AR: "Argentina",
  CL: "Chile",
  CO: "Colombia",
  ZA: "South Africa",
  EG: "Egypt",
  NG: "Nigeria",
  KE: "Kenya",
  BD: "Bangladesh",
  PK: "Pakistan",
  IR: "Iran",
  SA: "Saudi Arabia",
  AE: "UAE",
  IL: "Israel",
  HK: "Hong Kong",
  TW: "Taiwan",
  NZ: "New Zealand",
  MA: "Morocco",
}

// Short country names for compact displays
export const COUNTRY_NAMES_SHORT: Record<string, string> = {
  US: "USA",
  CA: "Canada",
  MX: "Mexico",
  BR: "Brazil",
  AR: "Argentina",
  GB: "UK",
  DE: "Germany",
  FR: "France",
  IT: "Italy",
  ES: "Spain",
  NL: "Netherlands",
  PL: "Poland",
  RU: "Russia",
  UA: "Ukraine",
  CN: "China",
  IN: "India",
  JP: "Japan",
  KR: "S. Korea",
  ID: "Indonesia",
  TH: "Thailand",
  VN: "Vietnam",
  MY: "Malaysia",
  SG: "Singapore",
  PH: "Philippines",
  TR: "Turkey",
  SA: "S. Arabia",
  AE: "UAE",
  IL: "Israel",
  HK: "Hong Kong",
  TW: "Taiwan",
  AU: "Australia",
  NZ: "N. Zealand",
  ZA: "S. Africa",
  EG: "Egypt",
  NG: "Nigeria",
}

// Map ISO country codes to continent codes
export const COUNTRY_TO_CONTINENT: Record<string, string> = {
  // North America
  US: "NA",
  CA: "NA",
  MX: "NA",
  // South America
  BR: "SA",
  AR: "SA",
  CL: "SA",
  CO: "SA",
  // Europe
  GB: "EU",
  DE: "EU",
  FR: "EU",
  IT: "EU",
  ES: "EU",
  NL: "EU",
  PL: "EU",
  RU: "EU",
  UA: "EU",
  // Asia
  CN: "AS",
  IN: "AS",
  JP: "AS",
  KR: "AS",
  ID: "AS",
  TH: "AS",
  VN: "AS",
  MY: "AS",
  SG: "AS",
  PH: "AS",
  TR: "AS",
  SA: "AS",
  AE: "AS",
  IL: "AS",
  PK: "AS",
  BD: "AS",
  IR: "AS",
  HK: "AS",
  TW: "AS",
  // Oceania
  AU: "OC",
  NZ: "OC",
  // Africa
  ZA: "AF",
  EG: "AF",
  NG: "AF",
  KE: "AF",
  MA: "AF",
}

// Get country name with fallback to code
export function getCountryName(code: string, short = false): string {
  if (short) {
    return COUNTRY_NAMES_SHORT[code] || COUNTRY_NAMES[code] || code
  }
  return COUNTRY_NAMES[code] || code
}

// Get continent code for a country
export function getContinent(countryCode: string): string {
  return COUNTRY_TO_CONTINENT[countryCode] || "AS" // Default to Asia if unknown
}
