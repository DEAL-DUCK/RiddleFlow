import axios from 'axios';

const state = {
  hackathons: null,
  hackathon: null
};

const getters = {
  stateHackathons: state => state.hackathons,
  stateHackathon: state => state.hackathon,
};

const actions = {
  async createHackathon({dispatch}, hackathon) {
    await axios.post('hackathons', hackathon);
    await dispatch('getHackathons');
  },
  async getHackathons({commit}) {
    let {data} = await axios.get('hackathons');
    commit('setHackathons', data);
  },
  async viewHackathon({commit}, id) {
    let {data} = await axios.get(`hackathon/${id}`);
    commit('setHackathon', data);
  },
  // eslint-disable-next-line no-empty-pattern
  async updateHackathon({}, hackathon) {
    await axios.patch(`hackathon/${hackathon.id}`, hackathon.form);
  },
  // eslint-disable-next-line no-empty-pattern
  async deleteHackathon({}, id) {
    await axios.delete(`hackathon/${id}`);
  }
};

const mutations = {
  setHackathons(state, hackathons){
    state.hackathons = hackathons;
  },
  setHackathon(state, hackathon){
    state.hackathon = hackathon;
  },
};

export default {
  state,
  getters,
  actions,
  mutations
};