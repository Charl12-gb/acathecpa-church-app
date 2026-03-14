import apiClient from './index';
import { 
    Course, CourseCreatePayload, CourseUpdatePayload, CourseStatus,
    CourseSection, CourseSectionCreatePayload, /* CourseSectionUpdatePayload, */ // Assuming full update payloads will be defined if needed
    CourseLesson, CourseLessonCreatePayload, /* CourseLessonUpdatePayload, */
    CourseTest, CourseTestCreatePayload, /* CourseTestUpdatePayload, */
    TestQuestion, TestQuestionCreatePayload, /* TestQuestionUpdatePayload, */
    // TestSubmissionPayload, TestResult, // Original types, might be replaced or kept for other uses
    Certificate, CertificateDisplay, CertificateBase, // Added Certificate types
    EnrollmentProgress, // Added for new progress endpoints
    TestSubmissionWithScoreSchema // Added for submitting test with score
} from '../../types/api';

// Define EnrollmentProgress and TestSubmissionWithScoreSchema in ../../types/api.ts if not already defined by backend schema generation
// For now, assuming they are compatible with backend schemas of the same name.

// === Courses ===
export const getAllCourses = async (params?: { skip?: number; limit?: number; status?: CourseStatus; sortBy?: string; sortOrder?: string }): Promise<Course[]> => {
  const response = await apiClient.get<Course[]>('/courses/', { params });
  return response.data;
};

export const getCourseById = async (courseId: number): Promise<Course> => {
  const response = await apiClient.get<Course>(`/courses/${courseId}`);
  return response.data;
};

export const getCourseTestById = async (testId: number): Promise<CourseTest> => {
    // Backend router for this: GET /courses/tests/{test_id}
    const response = await apiClient.get<CourseTest>(`/courses/tests/${testId}`);
    return response.data;
};

export const getCourseTestBySectionId = async (sectionId: number): Promise<CourseTest> => {
    // Backend router for this: GET /courses/sections/{section_id}/tests
    const response = await apiClient.get<CourseTest>(`/courses/sections/${sectionId}/tests`);
    return response.data;
};

export const createCourse = async (data: CourseCreatePayload): Promise<Course> => {
  const response = await apiClient.post<Course>('/courses/', data);
  return response.data;
};

export const updateCourse = async (courseId: number, data: CourseUpdatePayload): Promise<Course> => {
  const response = await apiClient.put<Course>(`/courses/${courseId}`, data);
  return response.data;
};

export const deleteCourse = async (courseId: number): Promise<Course> => { // Backend returns deleted course
  const response = await apiClient.delete<Course>(`/courses/${courseId}`);
  return response.data;
};

export const publishCourse = async (courseId: number): Promise<Course> => {
    const response = await apiClient.post<Course>(`/courses/${courseId}/publish`);
    return response.data;
};

// === Course Enrollment & Progress ===
export const enrollInCourse = async (courseId: number): Promise<any> => {
  const response = await apiClient.post(`/courses/${courseId}/enroll`);
  return response.data;
};

export const getMyCourseEnrollmentProgress = async (courseId: number): Promise<EnrollmentProgress> => {
    // Corresponds to GET /api/v1/courses/{course_id}/me/progress
    const response = await apiClient.get<EnrollmentProgress>(`/courses/${courseId}/me/progress`);
    return response.data;
};

export const unenrollFromCourse = async (courseId: number): Promise<any> => {
    const response = await apiClient.post(`/courses/${courseId}/unenroll`);
    return response.data;
};

export const getMyEnrolledCourses = async (params?: { skip?: number; limit?: number }): Promise<Course[]> => {
  const response = await apiClient.get<Course[]>('/courses/me/enrolled', { params });
  return response.data;
};

export const getInstructorCourses = async (params?: { skip?: number; limit?: number }): Promise<Course[]> => {
    const response = await apiClient.get<Course[]>('/courses/instructor/me', { params });
    return response.data;
};


// === Course Sections ===
export const createCourseSection = async (courseId: number, data: CourseSectionCreatePayload): Promise<CourseSection> => {
  const response = await apiClient.post<CourseSection>(`/courses/${courseId}/sections/`, data);
  return response.data;
};

export const getCourseSections = async (courseId: number, params?: { skip?: number; limit?: number }): Promise<CourseSection[]> => {
    const response = await apiClient.get<CourseSection[]>(`/courses/${courseId}/sections/`, { params });
    return response.data;
};

export const getCourseSectionById = async (sectionId: number): Promise<CourseSection> => {
    const response = await apiClient.get<CourseSection>(`/courses/sections/${sectionId}`);
    return response.data;
};

export const updateCourseSection = async (sectionId: number, data: Partial<CourseSectionCreatePayload>): Promise<CourseSection> => { // Use Partial for update
    const response = await apiClient.put<CourseSection>(`/courses/sections/${sectionId}`, data);
    return response.data;
};

export const deleteCourseSection = async (sectionId: number): Promise<CourseSection> => {
    const response = await apiClient.delete<CourseSection>(`/courses/sections/${sectionId}`);
    return response.data;
};


// === Course Lessons ===
export const createCourseLesson = async (sectionId: number, data: CourseLessonCreatePayload): Promise<CourseLesson> => {
  const response = await apiClient.post<CourseLesson>(`/courses/sections/${sectionId}/lessons/`, data);
  return response.data;
};

export const getCourseLessons = async (sectionId: number, params?: { skip?: number; limit?: number }): Promise<CourseLesson[]> => {
    const response = await apiClient.get<CourseLesson[]>(`/courses/sections/${sectionId}/lessons/`, { params });
    return response.data;
};

export const getCourseLessonById = async (lessonId: number): Promise<CourseLesson> => {
    const response = await apiClient.get<CourseLesson>(`/courses/lessons/${lessonId}`);
    return response.data;
};

export const updateCourseLesson = async (lessonId: number, data: Partial<CourseLessonCreatePayload>): Promise<CourseLesson> => { // Use Partial for update
    const response = await apiClient.put<CourseLesson>(`/courses/lessons/${lessonId}`, data);
    return response.data;
};

export const deleteCourseLesson = async (lessonId: number): Promise<CourseLesson> => {
    const response = await apiClient.delete<CourseLesson>(`/courses/lessons/${lessonId}`);
    return response.data;
};

export const markStudentLessonCompleted = async (courseId: number, lessonId: number): Promise<EnrollmentProgress> => {
  const response = await apiClient.post<EnrollmentProgress>(`/courses/${courseId}/lessons/${lessonId}/complete`);
  return response.data;
};

export const markStudentSectionCompleted = async (courseId: number, sectionId: number): Promise<EnrollmentProgress> => {
  const response = await apiClient.post<EnrollmentProgress>(`/courses/${courseId}/sections/${sectionId}/complete`);
  return response.data;
};


export const markLessonCompleted = async (lessonId: number): Promise<CourseLesson> => { // Return updated lesson
  const response = await apiClient.put<CourseLesson>(`/courses/lessons/${lessonId}`, { is_completed: true }); // Ensure 'is_completed' matches backend schema
  return response.data;
};

// === Course Tests ===
export const createCourseTest = async (sectionId: number, data: CourseTestCreatePayload): Promise<CourseTest> => {
    const response = await apiClient.post<CourseTest>(`/courses/sections/${sectionId}/tests/`, data);
    return response.data;
};

export const fetchFullCourseTest = async (testId: number): Promise<CourseTest> => {
    // Corresponds to GET /api/v1/courses/tests/{test_id}
    const response = await apiClient.get<CourseTest>(`/courses/tests/${testId}`);
    return response.data;
};

export const fetchCourseTestForSection = async (sectionId: number): Promise<CourseTest> => {
    // Corresponds to GET /api/v1/courses/sections/{section_id}/tests
    const response = await apiClient.get<CourseTest>(`/courses/sections/${sectionId}/tests`);
    return response.data;
};

export const updateCourseTest = async (testId: number, data: Partial<CourseTestCreatePayload>): Promise<CourseTest> => {
    const response = await apiClient.put<CourseTest>(`/courses/tests/${testId}`, data);
    return response.data;
};

export const deleteCourseTest = async (testId: number): Promise<CourseTest> => {
    const response = await apiClient.delete<CourseTest>(`/courses/tests/${testId}`);
    return response.data;
};

export const submitStudentTestAttempt = async (courseId: number, testId: number, submissionData: TestSubmissionWithScoreSchema): Promise<EnrollmentProgress> => {
    // Corresponds to POST /api/v1/courses/{course_id}/tests/{test_id}/attempt
    const response = await apiClient.post<EnrollmentProgress>(`/courses/${courseId}/tests/${testId}/attempt`, submissionData);
    return response.data;
};

// Original submitTestAnswers might be deprecated or used for a different flow if TestResult is a different shape
// export const submitTestAnswers = async (testId: number, data: TestSubmissionPayload): Promise<TestResult> => {
//     const response = await apiClient.post<TestResult>(`/courses/tests/${testId}/submit`, data);
//     return response.data;
// };


// === Test Questions (within a Test) ===
// Test questions are usually managed in the context of their test.
// Backend router provides: POST /tests/{test_id}/questions/, GET /questions/{question_id}, etc.

export const createTestQuestion = async (testId: number, data: TestQuestionCreatePayload): Promise<TestQuestion> => {
    const response = await apiClient.post<TestQuestion>(`/courses/tests/${testId}/questions/`, data);
    return response.data;
};

export const getTestQuestions = async (testId: number, params?: { skip?: number; limit?: number }): Promise<TestQuestion[]> => {
    const response = await apiClient.get<TestQuestion[]>(`/courses/tests/${testId}/questions/`, { params });
    return response.data;
};

export const getTestQuestionById = async (questionId: number): Promise<TestQuestion> => {
    const response = await apiClient.get<TestQuestion>(`/courses/questions/${questionId}`);
    return response.data;
};

export const updateTestQuestion = async (questionId: number, data: Partial<TestQuestionCreatePayload>): Promise<TestQuestion> => { // Use Partial
    const response = await apiClient.put<TestQuestion>(`/courses/questions/${questionId}`, data);
    return response.data;
};

export const deleteTestQuestion = async (questionId: number): Promise<TestQuestion> => {
    const response = await apiClient.delete<TestQuestion>(`/courses/questions/${questionId}`);
    return response.data;
};

// === Certificate API Functions ===

/**
 * Fetches all certificates for the currently authenticated user.
 * Corresponds to GET /users/{user_id}/certificates/ (user_id is derived by backend from auth token).
 * NOTE: The backend endpoint is /users/{user_id}/certificates/. For "my" certificates,
 * the frontend usually doesn't send user_id; backend infers it.
 * If your backend /users/{user_id}/certificates/ requires user_id even for self,
 * this needs an adjustment or a dedicated /me/certificates/ endpoint in backend.
 * For now, assuming a /me/certificates or similar, or that user_id is passed.
 * Let's assume for now the backend has a route like /users/me/certificates/
 * or the actual user ID needs to be passed. The plan had GET /users/{user_id}/certificates/
 * and the router implementation used current_user.id if it matched user_id.
 * We need a way to get current_user.id if it's for "self".
 * A common pattern is a dedicated /me/certificates endpoint or the frontend stores user_id.
 * For this task, let's assume a function getCurrentUserId() exists or it's passed.
 * Given the router `GET /users/{user_id}/certificates/` and its auth,
 * it's safer to assume it expects a user_id. For "my" certificates, a
 * wrapper in the store or component would call this with the current user's ID.
 * Let's define it to take userId, and the caller (e.g., store) provides it.
 */
export const getUserCertificates = async (userId: number): Promise<CertificateDisplay[]> => {
  const response = await apiClient.get<CertificateDisplay[]>(`/users/${userId}/certificates/`); // This path is from the original file. The new router uses /courses/users/{user_id}/certificates
  return response.data;
};

// New function based on the router for certificate check/issuance by student
export const triggerStudentCertificateCheck = async (courseId: number): Promise<CertificateDisplay | null> => {
    // Corresponds to POST /courses/{course_id}/me/check-certificate
    const response = await apiClient.post<CertificateDisplay | null>(`/courses/${courseId}/me/check-certificate`);
    return response.data;
};

/**
 * Fetches the current user's certificate for a specific course.
 * Corresponds to GET /courses/{course_id}/certificate
 */
export const getMyCertificateForCourse = async (courseId: number): Promise<CertificateDisplay | null> => {
  try {
    const response = await apiClient.get<CertificateDisplay>(`/courses/${courseId}/certificate`);
    return response.data; // Will be null if backend returns 200 with null body for no certificate
  } catch (error: any) {
    if (error.response && error.response.status === 404) {
      return null; // Treat 404 as "no certificate found"
    }
    throw error; // Re-throw other errors
  }
};

/**
 * Fetches a specific certificate by its ID.
 * Corresponds to GET /certificates/{certificate_id}
 */
export const getCertificateDetails = async (certificateId: number): Promise<Certificate> => {
  const response = await apiClient.get<Certificate>(`/certificates/${certificateId}`);
  return response.data;
};

/**
 * Manually issues a certificate for a user in a course.
 * Corresponds to POST /courses/{course_id}/users/{user_id}/certificates/
 * The backend currently auto-generates issue_date. If other fields for CertificateCreate
 * are needed from frontend, the payload here should be `CertificateBase` or similar.
 */
export const issueCertificateForUser = async (courseId: number, userId: number): Promise<Certificate> => {
  // The backend endpoint creates CertificateCreate internally.
  // No request body is defined in the router for this POST, so sending empty object.
  // If backend expects a body (e.g. certificate_url, verification_code), it needs to be added.
  const response = await apiClient.post<Certificate>(`/courses/${courseId}/users/${userId}/certificates/`, {}); // This path is from original.
  return response.data;
};
