// orval.config.ts
const OPENAPI_URL =
  process.env.OPENAPI_URL ?? 'http://localhost:8000/schema/openapi.json';

const config = {
  litestarBrowser: {
    output: {
      mode: 'tags-split',
      target: 'src/openapi',
      client: 'react-query',
      mock: false,
      override: {
        query: {
          useSuspenseQuery: true,
        },
        mutator: {
          path: 'src/openapi/custom-instance.ts',
          name: 'customInstance',
        },
      },
    },
    input: { target: OPENAPI_URL },
  },

  // SERVER: fetch client (no hooks)
  litestarServer: {
    output: {
      mode: 'single', // single file is handy server-side
      target: 'src/server-sdk.ts', // import from '@/server-sdk'
      client: 'fetch', // Edge/runtime friendly
      mock: false,
      override: {
        mutator: {
          path: 'src/server-mutator.ts',
          name: 'serverMutator',
        },
      },
    },
    input: { target: OPENAPI_URL },
  },
};

export default config;
