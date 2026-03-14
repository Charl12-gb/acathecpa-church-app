import { defineStore } from 'pinia';
import {
  Professor,
  ProfessorProfile,
  ProfessorProfileCreatePayload,
  ProfessorProfileUpdatePayload,
  ProfessorUserAndProfileCreatePayload,
  UserUpdatePayload,
} from '../types/api';

// Import API service functions with aliases to avoid name clashes if any
import {
  getProfessors as apiGetProfessors,
  getProfessor as apiGetProfessor,
  createProfessorProfile as apiCreateProfessorProfile,
  updateProfessorProfile as apiUpdateProfessorProfile,
  deleteProfessorProfile as apiDeleteProfessorProfile,
  createProfessorUserAndProfile as apiCreateProfessorUserAndProfile,
} from '../services/api/professor';

import {
  deleteUser as apiDeleteUser,
  updateUser as apiUpdateUser
} from '../services/api/user';

export interface ProfessorState {
  professors: Professor[];
  currentProfessor: Professor | null; // Professor type includes User + Profile
  isLoadingList: boolean;
  isLoadingItem: boolean;
  errorList: any; // Changed to any to match snippet
  errorItem: any; // Changed to any to match snippet
  totalPages: number; // Added from snippet
}

export const useProfessorStore = defineStore('professor', {
  state: (): ProfessorState => ({
    professors: [],
    currentProfessor: null,
    isLoadingList: false,
    isLoadingItem: false,
    errorList: null,
    errorItem: null,
    totalPages: 0, // Added from snippet
  }),

  getters: {
    getProfessorById: (state) => (id: number): Professor | undefined => {
      return state.professors.find((prof: Professor) => prof.id === id);
    },
    getAllProfessors: (state): Professor[] => {
      return state.professors;
    },
  },

  actions: {
    async fetchProfessors(params: { page?: number; limit?: number; [key: string]: any } = {}) { // params from snippet
      this.isLoadingList = true;
      this.errorList = null;
      try {
        // Adapting to snippet's expectation of apiGetProfessors
        const response = await apiGetProfessors(params);
        // Assuming response is an array directly, as per snippet's simplified handling
        this.professors = response;
        // If API returns { items: Professor[], total: number }
        // this.professors = response.items;
        // this.totalPages = Math.ceil(response.total / (params.limit || 10));
      } catch (error) {
        this.errorList = error; // Store the actual error object
        console.error("Error fetching professors:", error);
      } finally {
        this.isLoadingList = false;
      }
    },

    async fetchProfessor(userId: number) {
      this.isLoadingItem = true;
      this.errorItem = null;
      try {
        this.currentProfessor = await apiGetProfessor(userId);
      } catch (error) {
        this.errorItem = error; // Store the actual error object
        this.currentProfessor = null;
        console.error(`Error fetching professor ${userId}:`, error);
      } finally {
        this.isLoadingItem = false;
      }
    },

    // Action for creating a NEW USER and their Professor Profile
    async actionCreateProfessorUserAndProfile(payload: ProfessorUserAndProfileCreatePayload): Promise<Professor> {
      this.isLoadingItem = true;
      this.errorItem = null;
      try {
        const newProfessor = await apiCreateProfessorUserAndProfile(payload);
        this.currentProfessor = newProfessor; // Store the newly created professor
        // Optionally, refresh the list or add to it if maintaining a local list
        // For example, if the list should show the new professor immediately:
        // await this.fetchProfessors(); // Or this.professors.unshift(newProfessor);
        return newProfessor; // Return the new professor data for component handling
      } catch (error) {
        this.errorItem = error; // Store the actual error object
        console.error("Error creating professor user and profile:", error);
        throw error; // Re-throw to allow component to catch it
      } finally {
        this.isLoadingItem = false;
      }
    },

    // Existing action: Create profile for an EXISTING user
    async createProfile(userId: number, profileData: ProfessorProfileCreatePayload): Promise<ProfessorProfile | null> {
      this.isLoadingItem = true;
      this.errorItem = null;
      try {
        const newProfile = await apiCreateProfessorProfile(userId, profileData);
        if (this.currentProfessor && this.currentProfessor.id === userId) {
          await this.fetchProfessor(userId); // Refetch to get combined data
        } else {
          // If not current professor, or no current professor, clear/invalidate or fetch
           await this.fetchProfessor(userId); // Fetch anyway to update if it becomes current
        }
        // Also update in the list if present
        const professorIndex = this.professors.findIndex((p: Professor) => p.id === userId);
        if (professorIndex !== -1 && this.currentProfessor && (this.currentProfessor as any).id === userId) {
            this.professors[professorIndex] = { ...this.currentProfessor } as any;
        }
        return newProfile;
      } catch (error) {
        this.errorItem = error; // Store the actual error object
        console.error("Error creating professor profile:", error);
        throw error;
      } finally {
        this.isLoadingItem = false;
      }
    },

    async updateProfile(userId: number, profileData: ProfessorProfileUpdatePayload): Promise<ProfessorProfile | null> {
      this.isLoadingItem = true;
      this.errorItem = null;
      try {
        const updatedProfile = await apiUpdateProfessorProfile(userId, profileData);
        if (this.currentProfessor && (this.currentProfessor as any).id === userId) {
          // Update the profile part of the currentProfessor
          if ((this.currentProfessor as any).professor_profile) {
            (this.currentProfessor as any).professor_profile = {
              ...(this.currentProfessor as any).professor_profile,
              ...updatedProfile
            };
          } else {
            await this.fetchProfessor(userId); // Refetch if profile was missing
          }
        }
         // Also update in the list
        const professorIndex = this.professors.findIndex((p: Professor) => p.id === userId);
        if (professorIndex !== -1 && this.currentProfessor && (this.currentProfessor as any).id === userId) {
             this.professors[professorIndex] = { ...this.currentProfessor } as any; // Update with the fetched/updated professor
        } else if (professorIndex !== -1) { // If not current, but in list, update its profile part
            const profInList = this.professors[professorIndex];
            if (profInList.professor_profile) {
                (this.professors[professorIndex] as any).professor_profile = { ...profInList.professor_profile, ...updatedProfile};
            } else { // If profile was somehow missing, fetch that specific professor for the list
                const fetchedProf = await apiGetProfessor(userId);
                this.professors[professorIndex] = fetchedProf as any;
            }
        }
        return updatedProfile;
      } catch (error) {
        this.errorItem = error; // Store the actual error object
        console.error("Error updating professor profile:", error);
        throw error;
      } finally {
        this.isLoadingItem = false;
      }
    },

    async deleteProfile(userId: number) { // From snippet
      this.isLoadingItem = true;
      this.errorItem = null;
      try {
        await apiDeleteProfessorProfile(userId); // Using the aliased import
        if (this.currentProfessor && (this.currentProfessor as any).id === userId) {
          if ((this.currentProfessor as any).professor_profile) {
             (this.currentProfessor as any).professor_profile = null;
          }
        }
        // Update the list: find professor and set their profile to null or refetch
        const professorIndex = this.professors.findIndex((p: Professor) => p.id === userId);
        if (professorIndex !== -1) {
          if (this.professors[professorIndex].professor_profile) {
            this.professors[professorIndex].professor_profile = null;
          }
        }
      } catch (error) {
        this.errorItem = error; // Store the actual error object
        console.error("Error deleting professor profile:", error);
        throw error;
      } finally {
        this.isLoadingItem = false;
      }
    },

    async deleteProfessor(userId: number) { // From existing file
      this.isLoadingItem = true; // Aligning with other actions
      this.errorItem = null;
      try {
        await apiDeleteUser(userId); // This deletes the user
        this.professors = this.professors.filter((p: Professor) => p.id !== userId);
        if (this.currentProfessor && (this.currentProfessor as any).id === userId) {
          this.currentProfessor = null;
        }
      } catch (error: any) {
        this.errorItem = error; // Store the actual error object
        console.error("Error deleting professor (user):", error);
        throw error;
      } finally {
          this.isLoadingItem = false;
      }
    },

    async toggleProfessorStatus(userId: number, currentStatus: boolean) { // From existing file
      this.isLoadingItem = true; // Aligning with other actions
      this.errorItem = null;
      try {
        const payload: UserUpdatePayload = { is_active: !currentStatus };
        const updatedUser = await apiUpdateUser(userId, payload);

        const professorIndex = this.professors.findIndex((p: Professor) => p.id === userId);
        if (professorIndex !== -1) {
          this.professors[professorIndex].is_active = updatedUser.is_active || false;
        }
        if (this.currentProfessor && (this.currentProfessor as any).id === userId) {
          (this.currentProfessor as any).is_active = updatedUser.is_active || false;
        }
      } catch (error: any) {
        this.errorItem = error; // Store the actual error object
        console.error("Error toggling professor status:", error);
        throw error;
      } finally {
        this.isLoadingItem = false;
      }
    },

    clearCurrentProfessor() { // From snippet
      this.currentProfessor = null;
      this.errorItem = null;
    }
  },
});
