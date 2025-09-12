export default {
  litestar: {
    output: {
      mode: 'tags-split',
      target: 'src/openapi',
      client: 'react-query',
      mock: false,
    },
    input: {
      target: 'http://localhost:8000/schema/openapi.json',
    },
  },
};
