import { RESTDataSource } from "@apollo/datasource-rest";
import { DisplayType } from "../generated/schema";

export class SparseHistoryApi extends RESTDataSource {
  override baseURL = "http://localhost:8000";
  async getUsers() {
    return this.get("/users");
  }
  async getUser(id: string) {
    return this.get(`/users/${id}`);
  }
  async getUserRevisions(id: string, display: DisplayType) {
    return this.get(`/users/${id}/revisions`, {
      params: {
        display: display.toLocaleLowerCase(),
      },
    });
  }
  async getUserRevision(id: string, revisionId: string, display: DisplayType) {
    return this.get(`/users/${id}/revisions/${revisionId}`, {
      params: {
        display: display.toLocaleLowerCase(),
      },
    });
  }
}
