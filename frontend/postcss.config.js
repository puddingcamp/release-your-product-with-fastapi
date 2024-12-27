export default {
    plugins: {
        'postcss-import': {},
        'tailwindcss/nesting': 'postcss-nesting',
        tailwindcss: {
            config: './tailwind.config.js',
        },
        autoprefixer: {
            overrideBrowserslist: [
                'Android 4.1',
                'iOS 7.1',
                'Chrome > 31',
                'ff > 31',
                'ie >= 8',
                'last 10 versions',
            ],
            grid: true,
        },
        'postcss-preset-env': {
            features: { 'nesting-rules': false },
        },
    },
};
