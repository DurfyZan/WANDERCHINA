import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://xavbqoshoxcphdakeqbe.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhhdmJxb3Nob3hjcGhkYWtlcWJlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkyMTYxMTMsImV4cCI6MjA5NDc5MjExM30.vADCVT5DPgBFXLfjxd3Lybu8ddXafalziWNkLWGz1G8'

export const supabase = createClient(supabaseUrl, supabaseKey)