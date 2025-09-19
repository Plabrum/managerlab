const config = {
  litestar: {
    output: {
      mode: 'tags-split',
      target: 'src/openapi',
      client: 'react-query',
      mock: false,
      override: {
        mutator: {
          path: 'src/openapi/custom-instance.ts',
          name: 'customInstance',
        },
      },
    },
    input: {
      target: 'http://localhost:8000/schema/openapi.json',
    },
  },
};

export default config;
