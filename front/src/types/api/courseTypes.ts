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
  MULTIPLE_CHOICE = 'multiple_choice',
  ESSAY = 'essay',
}

export interface TestQuestion {
  id: number;
  test_id: number;
  question_type: QuestionType;
  question_text: string;
  options?: any[] | null; // e.g., [{id: string, text: string}]
  correct_answer_data?: any | null; // boolean for true/false, string/number for multiple, null for essay
  points: number;
}

export interface TestQuestionCreatePayload {
  question_type: QuestionType;
  question_text: string;
  points: number;
  options?: any[];
  correct_answer_data?: any;
  test_id?: number; // Set by backend if created with test
}

export interface TestQuestionUpdatePayload {
  question_type?: QuestionType;
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

export interface CourseTestUpdatePayload {
  title?: string;
  description?: string;
  duration_minutes?: number;
  passing_score?: number;
  max_attempts?: number;
  questions?: (TestQuestionCreatePayload | TestQuestionUpdatePayload | { id: number })[];
}

export interface CourseLesson {
  id: number;
  section_id: number;
  title: string;
  type: LessonType;
  content_body?: string | null;
  video_url?: string | null;
  duration?: string | null;
  order: number;
  is_completed: boolean;
}

export interface CourseLessonCreatePayload {
  title: string;
  type: LessonType;
  content_body?: string;
  video_url?: string;
  duration?: string;
  order?: number;
  section_id?: number;
}

export interface CourseLessonUpdatePayload {
  title?: string;
  type?: LessonType;
  content_body?: string;
  video_url?: string;
  duration?: string;
  order?: number;
  is_completed?: boolean;
}

export interface CourseSection {
  id: number;
  course_id: number;
  title: string;
  description?: string | null;
  order: number;
  content_type: string;
  video_url?: string | null;
  text_content?: string | null;
  lessons: CourseLesson[];
  test?: CourseTest | null;
}

export interface CourseSectionCreatePayload {
  title: string;
  description?: string;
  order?: number;
  content_type: string;
  video_url?: string;
  text_content?: string;
  course_id?: number;
  lessons?: CourseLessonCreatePayload[];
  test?: CourseTestCreatePayload;
}

export interface CourseSectionUpdatePayload {
  title?: string;
  description?: string;
  order?: number;
  content_type?: string;
  video_url?: string;
  text_content?: string;
  lessons?: (CourseLessonCreatePayload | CourseLessonUpdatePayload | { id: number })[];
  test?: (CourseTestCreatePayload | CourseTestUpdatePayload | { id: number });
}

export interface Course {
  id: number;
  title: string;
  description?: string | null;
  instructor_id: number;
  instructor: User;
  status: CourseStatus;
  created_at: string;
  updated_at: string;
  sections: CourseSection[];
  price?: number | null;
  is_free?: boolean;
  category: string;
  level: string;
  short_description?: string | null;
  image_url?: string | null;
  objectives: string[];
  prerequisites: string[];
  progress?: number;
}

export interface CourseCreatePayload {
  title: string;
  description?: string;
  status?: CourseStatus;
  price?: number;
  is_free?: boolean;
  category?: string;
  level?: string;
  short_description?: string;
  image_url?: string;
  objectives?: string[];
  prerequisites?: string[];
  sections?: CourseSectionCreatePayload[];
}

export interface CourseUpdatePayload {
  title?: string;
  description?: string;
  status?: CourseStatus;
  price?: number;
  is_free?: boolean;
  category?: string;
  level?: string;
  short_description?: string;
  image_url?: string;
  objectives?: string[];
  prerequisites?: string[];
  instructor_id?: number;
  sections?: (CourseSectionCreatePayload | CourseSectionUpdatePayload | { id: number })[];
}

export interface TestAnswerPayload {
    question_id: number;
    answer: any;
}

export interface TestSubmissionPayload {
    answers: TestAnswerPayload[];
}

export interface TestResult {
    score: number;
    passed: boolean;
}

export interface CertificateBase {
  course_id: number;
  user_id: number;
  issue_date: string;
  certificate_url?: string | null;
  verification_code?: string | null;
}

export interface Certificate extends CertificateBase {
  id: number;
  course: Course;
}

export interface CertificateDisplay {
  id: number;
  course_id: number;
  course_title: string;
  course_image_url?: string | null;
  issue_date: string;
  certificate_url?: string | null;
  verification_code?: string | null;
}

export interface EnrollmentProgress {
  user_id: number;
  course_id: number;
  enrolled_at: string;
  progress_percentage: number;
  completed_at?: string | null;
  completed_lessons: number[];
  completed_sections: number[];
  test_attempts: any[];
  test_scores: any[];
}

export interface TestQuestionAttemptSummaryInputSchema {
    question_id: number;
    is_correct?: boolean | null;
    points_earned?: number | null;
}

export interface TestSubmissionWithScoreSchema {
    score: number;
    passed: boolean;
    questions_summary?: TestQuestionAttemptSummaryInputSchema[] | null;
}
