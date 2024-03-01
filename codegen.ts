import { CodegenConfig } from "@graphql-codegen/cli";

const config: CodegenConfig = {
  schema: "./sparse_history/graphql/schema.gql",
  generates: {
    "./sparse_history/graphql/generated/schema.ts": {
      config: {
        useIndexSignature: true,
      },
      plugins: ["typescript", "typescript-resolvers"],
    },
  },
};

export default config;
