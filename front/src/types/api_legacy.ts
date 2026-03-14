// In front/src/types/api.ts (or similar)

// Added as per subtask
export interface QuestionOption {
  text: string;
  is_correct: boolean;
}

// RENAMED TYPE
export type CourseSectionType = 'video' | 'text' | 'quiz';

export interface CertificateBase {
  course_id: number;
  user_id: number;
  issue_date: string; // Dates are often strings in JSON
  certificate_url?: string | null;
  verification_code?: string | null;
}

export interface Certificate extends CertificateBase {
  id: number;
  course: Course; // Added to reflect backend eager loading
}

export interface CertificateDisplay { // For lists or summaries
  id: number;
  course_id: number;
  course_title: string; // Assuming this will now be populated from the nested course
  course_image_url?: string | null; // Adding for potential display
  issue_date: string;
  certificate_url?: string | null;
  verification_code?: string | null;
}

// Course Related Types
export enum LessonType {
  VIDEO = "video",
  TEXT = "text",
  QUIZ = "quiz",
}

export interface CourseLesson {
  id: number;
  title: string;
  type: LessonType;
  content_body?: string | null; // For text content
  video_url?: string | null;    // For video content
  quiz_data?: any;              // For quiz content (can be a more specific type)
  duration?: string | null;
  order: number;
  is_completed: boolean;
  section_id: number;
}

export interface CourseSection {
    id: number;
    title: string;
    lessons: CourseLesson[];
    order: number;
    content_type: CourseSectionType; // UPDATED
    video_url?: string | null;
    video_file_path?: string | null;
    text_content?: string | null;
    test?: CourseTest | null;
}

export interface User { // Basic User structure for instructor display
    id: number;
    name: string;
    // email?: string; // if needed
}

export interface Course {
    id: number;
    title: string;
    description?: string | null;
    instructor_id: number;
    instructor: User; // Assuming instructor details are nested or joined
    sections: CourseSection[];
    status: CourseStatus;
    created_at: string;
    updated_at: string;
    price?: number; // Added
    is_free?: boolean; // Added
    category: string;
    level: string;
    short_description?: string | null; // Added
    image_url?: string | null; // Renamed from image
    objectives?: string[] | null; // Added
    prerequisites?: string[] | null; // Added
    progress?: number; // Often calculated or comes with user-specific course data
}

// Payloads for creation/update if different from the main types
export interface CourseCreatePayload {
    title: string;
    description?: string | null;
    // instructor_id is usually set by backend based on current user
    // New fields for CourseCreatePayload (optional to match backend defaults)
    price?: number; // Added
    is_free?: boolean; // Added
    short_description?: string; // Added
    image_url?: string; // Added
    objectives?: string[]; // Added
    prerequisites?: string[]; // Added
}

export interface CourseUpdatePayload {
    title?: string;
    description?: string | null;
    status?: CourseStatus;
    // other updatable fields
    // New fields for CourseUpdatePayload (all optional)
    price?: number; // Added
    is_free?: boolean; // Added
    short_description?: string; // Added
    image_url?: string; // Added
    objectives?: string[]; // Added
    prerequisites?: string[]; // Added
}

export enum CourseStatus {
    DRAFT = "draft",
    PUBLISHED = "published",
}

export interface CourseSectionCreatePayload {
    title: string;
    order?: number;
    content_type: CourseSectionType; // UPDATED (required for create)
    video_url?: string;
    video_file_path?: string;
    text_content?: string;
    test?: CourseTestCreatePayload | null;
}

export interface CourseSectionUpdatePayload {
    title?: string;
    order?: number;
    content_type?: CourseSectionType; // UPDATED
    video_url?: string;
    video_file_path?: string;
    text_content?: string;
    test?: CourseTestUpdatePayload | null;
}

export interface CourseLessonCreatePayload {
    title: string;
    type: LessonType;
    content_body?: string | null;
    video_url?: string | null;
    quiz_data?: any;
    duration?: string | null;
    order?: number;
    is_completed?: boolean; // Allow setting on create if needed
    section_id: number; // Required for creation
}

export interface CourseLessonUpdatePayload {
    title?: string;
    type?: LessonType;
    content_body?: string | null;
    video_url?: string | null;
    quiz_data?: any;
    duration?: string | null;
    order?: number;
    is_completed?: boolean;
}


// Test related types (minimal example for completeness)
export interface CourseTest {
    id: number;
    title: string;
    description?: string | null;
    duration_minutes?: number; // minutes
    passing_score?: number; // percentage
    max_attempts?: number; // Added to match form
    questions: TestQuestion[];
}

export interface TestQuestion {
    id: number;
    question_text: string; // This is the question itself - kept as `text` to match existing
    question_type: string; // Name matches backend model field
    options?: QuestionOption[]; // Updated to use QuestionOption
    correct_answer_data?: any; // Renamed from correct_answer to match backend
    points?: number;
}

// Payloads for Test Creation/Update
export interface CourseTestCreatePayload {
    title: string;
    description?: string | null;
    duration_minutes?: number;
    passing_score?: number;
    max_attempts?: number;
    section_id: number; // Required to link test to a section
    questions?: TestQuestionCreatePayload[]; // Added to match backend schema
}

export interface CourseTestUpdatePayload {
    title?: string;
    description?: string | null;
    duration_minutes?: number;
    passing_score?: number;
    max_attempts?: number;
}

export interface TestQuestionCreatePayload {
    question_text: string;
    question_type: string; // Name matches backend model field
    options?: QuestionOption[]; // Updated (QuestionOption implies {text, is_correct})
    correct_answer_data?: any; // Renamed
    points?: number;
    test_id: number; // Required to link question to a test
}

export interface TestQuestionUpdatePayload {
    question_text?: string;
    question_type?: string; // Name matches backend model field
    options?: QuestionOption[]; // Updated
    correct_answer_data?: any; // Renamed
    points?: number;
}


export interface TestSubmissionPayload {
    answers: Array<{ question_id: number; answer: any }>; // Define 'any' more strictly if possible
}

export interface TestResult {
    score: number;
    passed: boolean;
    results: Array<{
        question_id: number;
        answer: any;
        is_correct: boolean;
        // correct_answer?: any; // Optionally send correct answer for review
    }>;
    // ... other result details
}

// --- Added for Enrollment Progress & Test Submissions ---

// Mirrors backend schemas/enrollment.py TestAttemptQuestionSummary
export interface TestAttemptQuestionSummary {
  question_id: number;
  is_correct?: boolean | null;
  points_earned?: number | null;
  // answer_provided?: any; // Optional: if you want to store what was answered
}

// Mirrors backend schemas/enrollment.py TestAttemptSchema
export interface TestAttempt {
  test_id: number;
  score: number;
  passed: boolean;
  attempted_at: string; // ISO datetime string
  questions_summary?: TestAttemptQuestionSummary[] | null;
  // attempt_number?: number; // Could be added if backend provides it
}

// Mirrors backend schemas/enrollment.py TestScoreSchema
export interface TestScore {
  test_id: number;
  score: number;
  // points_awarded?: number | null;
}

// Mirrors backend models/enrollments.py Enrollment and schemas/enrollment.py EnrollmentProgress
export interface EnrollmentProgress {
  user_id: number;
  course_id: number;
  enrolled_at: string; // ISO datetime string
  progress_percentage: number;
  completed_at?: string | null; // ISO datetime string
  completed_lessons: number[];
  completed_sections: number[];
  test_attempts: TestAttempt[];
  test_scores: TestScore[];
}

// Mirrors backend schemas/course_test.py TestQuestionAttemptSummaryInputSchema
export interface TestQuestionAttemptSummaryInputSchema {
    question_id: number;
    is_correct?: boolean | null;
    points_earned?: number | null;
}

// Mirrors backend schemas/course_test.py TestSubmissionWithScoreSchema
export interface TestSubmissionWithScoreSchema {
    score: number;
    passed: boolean;
    questions_summary?: TestQuestionAttemptSummaryInputSchema[] | null;
}
