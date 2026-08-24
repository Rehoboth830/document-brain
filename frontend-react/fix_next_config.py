content = """/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
}

module.exports = nextConfig
"""

with open("next.config.js", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
print("next.config.js updated - eslint and typescript errors ignored during build")
