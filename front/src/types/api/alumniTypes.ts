export interface Alumnus {
  id: number;
  name: string;
  country?: string | null;
  certificates_count: number;
  formations: string[];
}
