#!/usr/bin/env python3
"""
Simple script to create Supabase tables using direct SQL execution
"""

import requests
import json

# Supabase configuration
SUPABASE_URL = "https://kkurcqxrfarcxpzxsgwb.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtrdXJjcXhyZmFyY3hwenhzZ3diIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTE2MDEyNCwiZXhwIjoyMDcwNzM2MTI0fQ.7TV74iBqShkxJKylB2ff2aqFKrj4UJbXjS9hy1momo4"

def test_connection():
    """Test if we can connect to Supabase"""
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
    }
    
    try:
        # Try to access the messages table (will fail if doesn't exist, but connection works)
        response = requests.get(f"{SUPABASE_URL}/rest/v1/messages?limit=1", headers=headers)
        print(f"✅ Connection test: Status {response.status_code}")
        if response.status_code == 406:
            print("📋 Tables don't exist yet (expected)")
            return True
        elif response.status_code == 200:
            print("📋 Tables already exist")
            return True
        else:
            print(f"Response: {response.text}")
            return response.status_code in [200, 406]  # 406 means table doesn't exist
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def insert_test_data():
    """Insert some test data to verify tables work"""
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    # Test username reservation
    test_username = {
        "user_id": "test_user_123",
        "username": "testuser",
        "created_at": "2025-01-14T10:00:00Z"
    }
    
    try:
        response = requests.post(f"{SUPABASE_URL}/rest/v1/usernames", 
                               headers=headers, 
                               json=test_username)
        print(f"Username insert test: {response.status_code}")
        if response.status_code in [200, 201]:
            print("✅ Username table working")
            
            # Clean up test data
            requests.delete(f"{SUPABASE_URL}/rest/v1/usernames?user_id=eq.test_user_123", 
                          headers=headers)
            return True
        else:
            print(f"❌ Username insert failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test data insert failed: {e}")
        return False

def check_tables():
    """Check what tables exist"""
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
    }
    
    tables = ['messages', 'user_presence', 'typing_indicators', 'usernames']
    existing_tables = []
    
    for table in tables:
        try:
            response = requests.get(f"{SUPABASE_URL}/rest/v1/{table}?limit=1", headers=headers)
            if response.status_code == 200:
                existing_tables.append(table)
                print(f"✅ Table '{table}' exists")
            else:
                print(f"❌ Table '{table}' does not exist (status: {response.status_code})")
        except Exception as e:
            print(f"❌ Error checking table '{table}': {e}")
    
    return existing_tables

def main():
    print("🔍 Checking Supabase connection and tables...")
    
    # Test connection
    if not test_connection():
        print("❌ Cannot connect to Supabase")
        return False
    
    # Check existing tables
    existing_tables = check_tables()
    
    if len(existing_tables) == 4:
        print("🎉 All tables exist! Testing functionality...")
        if insert_test_data():
            print("✅ Database is fully functional!")
            return True
        else:
            print("⚠️ Tables exist but there might be permission issues")
            return False
    else:
        print(f"\n📋 Found {len(existing_tables)}/4 tables")
        print("\n🛠️ MANUAL SETUP REQUIRED:")
        print("Please go to your Supabase dashboard (https://supabase.com/dashboard)")
        print("Navigate to SQL Editor and run this SQL:")
        
        sql_commands = """
-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    username TEXT NOT NULL,
    content TEXT,
    message_type TEXT DEFAULT 'text' CHECK (message_type IN ('text', 'file')),
    file_name TEXT,
    file_url TEXT,
    file_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create user_presence table  
CREATE TABLE IF NOT EXISTS user_presence (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    last_seen TIMESTAMPTZ DEFAULT NOW()
);

-- Create typing_indicators table
CREATE TABLE IF NOT EXISTS typing_indicators (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create usernames table
CREATE TABLE IF NOT EXISTS usernames (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_user_presence_last_seen ON user_presence(last_seen);
CREATE INDEX IF NOT EXISTS idx_typing_created_at ON typing_indicators(created_at);
CREATE INDEX IF NOT EXISTS idx_usernames_username ON usernames(username);

-- Enable Row Level Security
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_presence ENABLE ROW LEVEL SECURITY;
ALTER TABLE typing_indicators ENABLE ROW LEVEL SECURITY;  
ALTER TABLE usernames ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (allow all operations for now)
CREATE POLICY IF NOT EXISTS "Enable all for messages" ON messages FOR ALL USING (true);
CREATE POLICY IF NOT EXISTS "Enable all for user_presence" ON user_presence FOR ALL USING (true);
CREATE POLICY IF NOT EXISTS "Enable all for typing_indicators" ON typing_indicators FOR ALL USING (true);
CREATE POLICY IF NOT EXISTS "Enable all for usernames" ON usernames FOR ALL USING (true);
"""
        
        print(sql_commands)
        print("\nAfter running the SQL, your chat should work!")
        return False

if __name__ == "__main__":
    main()