/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    images: {
        domains: ['localhost'],
    },
    async rewrites() {
        return [
            {
                source: '/ws',
                destination: 'http://localhost:9001',
            },
        ];
    },
};

module.exports = nextConfig;