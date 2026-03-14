import { User } from './userTypes';

export enum CourseStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
}

export enum LessonType {
  VIDEO = 'video',
  TEXT = 'text',
  QUIZ = 'quiz',
}

export enum QuestionType {
  MULTIPLE = 'multiple',
  TRUE_FALSE = 'true_false',
  ESSAY = 'essay',
}

export interface TestQuestion {
  id: number;
  test_id: number;
  type: QuestionType;
  question_text: string;
  options?: any[] | null; // e.g., [{id: string, text: string}]
  correct_answer_data?: any | null; // boolean for true/false, string/number for multiple, null for essay
  points: number;
}

export interface TestQuestionCreatePayload {
  type: QuestionType;
  question_text: string;
  points: number;
  options?: any[];
  correct_answer_data?: any;
  test_id?: number; // Set by backend if created with test
}

export interface TestQuestionUpdatePayload { // Added for completeness
  type?: QuestionType;
  question_text?: string;
  points?: number;
  options?: any[];
  correct_answer_data?: any;
}

export interface CourseTest {
  id: number;
  section_id?: number | null;
  title: string;
  description?: string | null;
  duration_minutes?: number | null;
  passing_score?: number | null;
  max_attempts?: number | null;
  questions: TestQuestion[];
}

export interface CourseTestCreatePayload {
  title: string;
  description?: string;
  duration_minutes?: number;
  passing_score?: number;
  max_attempts?: number;
  section_id?: number; // Optional: link to section
  questions?: TestQuestionCreatePayload[];
}

export interface CourseTestUpdatePayload { // Added for completeness
  title?: string;
  description?: string;
  duration_minutes?: number;
  passing_score?: number;
  max_attempts?: number;
  questions?: (TestQuestionCreatePayload | TestQuestionUpdatePayload | { id: number })[]; // Allow full update/create/delete logic
}

export interface CourseLesson {
  id: number;
  section_id: number;
  title: string;
  type: LessonType;
  content_body?: string | null;
  duration?: string | null; // e.g., "10:30"
  order: number;
  // completed: boolean; // This is user-specific, often handled in a separate UserLessonProgress model/table
}

export interface CourseLessonCreatePayload {
  title: string;
  type: LessonType;
  content_body?: string;
  duration?: string;
  order?: number;
  section_id?: number; // Set by backend if created with section
}

export interface CourseLessonUpdatePayload { // Added for completeness
  title?: string;
  type?: LessonType;
  content_body?: string;
  duration?: string;
  order?: number;
}

export interface CourseSection {
  id: number;
  course_id: number;
  title: string;
  description?: string | null;
  order: number;
  lessons: CourseLesson[];
  test?: CourseTest | null;
}

export interface CourseSectionCreatePayload {
  title: string;
  description?: string;
  order?: number;
  course_id?: number; // Set by backend if created with course
  lessons?: CourseLessonCreatePayload[];
  test?: CourseTestCreatePayload;
}

export interface CourseSectionUpdatePayload { // Added for completeness
  title?: string;
  description?: string;
  order?: number;
  lessons?: (CourseLessonCreatePayload | CourseLessonUpdatePayload | { id: number })[];
  test?: (CourseTestCreatePayload | CourseTestUpdatePayload | { id: number });
}

export interface Course {
  id: number;
  title: string;
  description?: string | null;
  instructor_id: number;
  instructor?: User | null;
  status: CourseStatus;
  created_at: string; // Or Date
  updated_at: string; // Or Date
  sections: CourseSection[];
  // progress?: number; // User-specific, from an enrollment object perhaps
}

export interface CourseCreatePayload {
  title: string;
  description?: string;
  status?: CourseStatus;
  // instructor_id is set by backend
  sections?: CourseSectionCreatePayload[]; // Allow creating sections with course
}

export interface CourseUpdatePayload {
  title?: string;
  description?: string;
  status?: CourseStatus;
  instructor_id?: number; // Allow changing instructor by admin
  sections?: (CourseSectionCreatePayload | CourseSectionUpdatePayload | { id: number })[]; // Allow updating sections
}

// For submitting test answers
export interface TestAnswerPayload {
    question_id: number;
    answer: any; // string, number, boolean depending on question type
}

export interface TestSubmissionPayload {
    answers: TestAnswerPayload[];
}

export interface TestResult {
    score: number;
    passed: boolean;
    // ... other result details
}
