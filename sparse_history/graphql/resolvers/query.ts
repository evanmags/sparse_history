import { QueryResolvers } from "../generated/schema";

export const Query: QueryResolvers = {
  users: (_, __, { dataSources }) => {
    return dataSources.sparseHistoryApi.getUsers();
  },
  user: (_, { id }, { dataSources }) => {
    return dataSources.sparseHistoryApi.getUser(id);
  },
  userRevisions: (_, { id, display }, { dataSources }) => {
    return dataSources.sparseHistoryApi.getUserRevisions(id, display);
  },
  userRevision: (_, { userId, revisionId, display }, { dataSources }) => {
    return dataSources.sparseHistoryApi.getUserRevision(
      userId,
      revisionId,
      display,
    );
  },
};
