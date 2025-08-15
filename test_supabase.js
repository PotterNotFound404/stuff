// Test Supabase connection in Node.js environment
const { createClient } = require('@supabase/supabase-js');

const SUPABASE_URL = 'https://kkurcqxrfarcxpzxsgwb.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtrdXJjcXhyZmFyY3hwenhzZ3diIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUxNjAxMjQsImV4cCI6MjA3MDczNjEyNH0.wRZyx1c8aH0u6Sek4oFeFM6yIi5mOgSWLl91XNbgbN4';

async function testConnection() {
    const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    
    try {
        console.log('Testing Supabase connection...');
        
        // Test basic connection
        const { data, error } = await supabase.auth.getSession();
        console.log('Auth test:', error ? `Error: ${error.message}` : 'Success');
        
        // Test table access
        const { data: messages, error: messagesError } = await supabase
            .from('messages')
            .select('*')
            .limit(1);
            
        if (messagesError) {
            console.log('Messages table error:', messagesError.message);
            if (messagesError.code === '42P01') {
                console.log('❌ Tables do not exist - need to create them manually');
            }
        } else {
            console.log('✅ Messages table accessible');
        }
        
    } catch (error) {
        console.error('Connection test failed:', error);
    }
}

testConnection();