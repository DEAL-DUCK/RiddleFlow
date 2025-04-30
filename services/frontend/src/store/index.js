import { createStore } from "vuex";

import notes from './modules/hackathons';

export default createStore({
  modules: {
    hackathons,
  }
});