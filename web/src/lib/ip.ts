/**
 * IP address utilities with IPv4 and IPv6 support
 */

export function isIPv4(ip: string): boolean {
  const parts = ip.split('.')
  if (parts.length !== 4) return false
  return parts.every(part => {
    const num = parseInt(part, 10)
    return !isNaN(num) && num >= 0 && num <= 255 && part === String(num)
  })
}

export function isIPv6(ip: string): boolean {
  // Basic IPv6 validation - matches full form and compressed forms
  const ipv6Regex = /^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::([0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4}$|^([0-9a-fA-F]{1,4}:){1,6}::([0-9a-fA-F]{1,4}:){0,5}[0-9a-fA-F]{1,4}$|^([0-9a-fA-F]{1,4}:){1,7}:$|^::[0-9a-fA-F]{1,4}$|^::$/
  return ipv6Regex.test(ip)
}

/**
 * Convert IPv4 to a comparable number
 */
function ipv4ToNumber(ip: string): number {
  const parts = ip.split('.').map(Number)
  return parts.reduce((acc, part) => (acc << 8) + part, 0) >>> 0
}

/**
 * Convert IPv6 to a comparable BigInt
 */
function ipv6ToBigInt(ip: string): bigint {
  // Expand compressed notation (::)
  let expanded = ip
  if (ip.includes('::')) {
    const parts = ip.split('::')
    const left = parts[0] ? parts[0].split(':') : []
    const right = parts[1] ? parts[1].split(':') : []
    const missing = 8 - left.length - right.length
    const middle = Array(missing).fill('0')
    expanded = [...left, ...middle, ...right].join(':')
  }
  
  const parts = expanded.split(':')
  let result = BigInt(0)
  for (const part of parts) {
    result = (result << BigInt(16)) + BigInt(parseInt(part || '0', 16))
  }
  return result
}

/**
 * Compare two IP addresses numerically
 * Returns: negative if a < b, positive if a > b, 0 if equal
 */
export function compareIPs(a: string, b: string): number {
  const aIsV4 = isIPv4(a)
  const bIsV4 = isIPv4(b)
  
  // If both are same type, compare normally
  if (aIsV4 && bIsV4) {
    return ipv4ToNumber(a) - ipv4ToNumber(b)
  }
  
  if (!aIsV4 && !bIsV4) {
    const aNum = ipv6ToBigInt(a)
    const bNum = ipv6ToBigInt(b)
    if (aNum < bNum) return -1
    if (aNum > bNum) return 1
    return 0
  }
  
  // Mixed types: IPv4 comes before IPv6
  return aIsV4 ? -1 : 1
}
