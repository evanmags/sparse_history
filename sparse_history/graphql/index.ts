import { join } from "path";
import { ApolloServer } from "@apollo/server";
import { startStandaloneServer } from "@apollo/server/standalone";
import { GraphQLFileLoader } from "@graphql-tools/graphql-file-loader";
import { loadSchema } from "@graphql-tools/load";
import { addResolversToSchema } from "@graphql-tools/schema";

import { Resolvers } from "./generated/schema";

import { Query } from "./resolvers/query.js";
import { SparseHistoryApi } from "./datasources/sparse_history_api.js";

const schema = await loadSchema(
  join(import.meta.dirname, "../../../sparse_history/graphql/schema.gql"),
  {
    loaders: [new GraphQLFileLoader()],
  },
);

const resolvers: Resolvers = {
  Query,
  RevisionReturn: {
    __resolveType(parent) {
      if (parent["created_at"]) {
        return "User";
      }
      return "UserRevision";
    },
  },
};

const schemaWithResolvers = addResolversToSchema({ schema, resolvers });

const server = new ApolloServer({
  schema: schemaWithResolvers,
});

const { url } = await startStandaloneServer(server, {
  listen: { port: 4000 },
  context: async () => {
    const { cache } = server;
    return {
      dataSources: {
        sparseHistoryApi: new SparseHistoryApi({ cache }),
      },
    };
  },
});

console.log(`🚀  Server ready at: ${url}`);
