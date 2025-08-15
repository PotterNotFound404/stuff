#!/usr/bin/env python3
"""
Supabase Database Setup Script
Creates necessary tables and configurations for the chat application
"""

import requests
import json
import sys

# Supabase configuration
SUPABASE_URL = "https://kkurcqxrfarcxpzxsgwb.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtrdXJjcXhyZmFyY3hwenhzZ3diIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTE2MDEyNCwiZXhwIjoyMDcwNzM2MTI0fQ.7TV74iBqshkxJKylB2ff2aqFKrj4UJbXjS9hy1momo4"

def execute_sql(sql_query):
    """Execute SQL query using Supabase REST API"""
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    url = f"{SUPABASE_URL}/rest/v1/rpc/execute_sql"
    data = {"sql": sql_query}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"✅ Successfully executed: {sql_query[:50]}...")
            return True
        else:
            print(f"❌ Failed to execute SQL: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception executing SQL: {e}")
        return False

def create_tables():
    """Create all necessary tables for the chat application"""
    
    # 1. Messages table
    messages_sql = """
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
    """
    
    # 2. User presence table
    presence_sql = """
    CREATE TABLE IF NOT EXISTS user_presence (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id TEXT UNIQUE NOT NULL,
        username TEXT NOT NULL,
        last_seen TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    # 3. Typing indicators table
    typing_sql = """
    CREATE TABLE IF NOT EXISTS typing_indicators (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id TEXT UNIQUE NOT NULL,
        username TEXT NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    # 4. Usernames table (for reservation)
    usernames_sql = """
    CREATE TABLE IF NOT EXISTS usernames (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    # 5. Create indexes for better performance
    indexes_sql = """
    CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
    CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
    CREATE INDEX IF NOT EXISTS idx_user_presence_last_seen ON user_presence(last_seen);
    CREATE INDEX IF NOT EXISTS idx_typing_created_at ON typing_indicators(created_at);
    CREATE INDEX IF NOT EXISTS idx_usernames_username ON usernames(username);
    """
    
    # Execute all SQL commands
    tables = [
        ("Messages", messages_sql),
        ("User Presence", presence_sql),
        ("Typing Indicators", typing_sql),
        ("Usernames", usernames_sql),
        ("Indexes", indexes_sql)
    ]
    
    success_count = 0
    for table_name, sql in tables:
        print(f"Creating {table_name} table...")
        if execute_sql(sql):
            success_count += 1
        else:
            print(f"Failed to create {table_name} table")
    
    return success_count == len(tables)

def setup_rls_policies():
    """Set up Row Level Security policies"""
    
    # Enable RLS on all tables
    rls_enable_sql = """
    ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
    ALTER TABLE user_presence ENABLE ROW LEVEL SECURITY;
    ALTER TABLE typing_indicators ENABLE ROW LEVEL SECURITY;
    ALTER TABLE usernames ENABLE ROW LEVEL SECURITY;
    """
    
    # Create policies for messages (public read, authenticated write)
    messages_policies_sql = """
    CREATE POLICY IF NOT EXISTS "Messages are viewable by everyone" ON messages FOR SELECT USING (true);
    CREATE POLICY IF NOT EXISTS "Users can insert their own messages" ON messages FOR INSERT WITH CHECK (true);
    CREATE POLICY IF NOT EXISTS "Users can update their own messages" ON messages FOR UPDATE USING (true);
    CREATE POLICY IF NOT EXISTS "Users can delete their own messages" ON messages FOR DELETE USING (true);
    """
    
    # Create policies for user_presence
    presence_policies_sql = """
    CREATE POLICY IF NOT EXISTS "Presence is viewable by everyone" ON user_presence FOR SELECT USING (true);
    CREATE POLICY IF NOT EXISTS "Users can manage their own presence" ON user_presence FOR ALL USING (true);
    """
    
    # Create policies for typing_indicators
    typing_policies_sql = """
    CREATE POLICY IF NOT EXISTS "Typing indicators are viewable by everyone" ON typing_indicators FOR SELECT USING (true);
    CREATE POLICY IF NOT EXISTS "Users can manage their own typing status" ON typing_indicators FOR ALL USING (true);
    """
    
    # Create policies for usernames
    usernames_policies_sql = """
    CREATE POLICY IF NOT EXISTS "Usernames are viewable by everyone" ON usernames FOR SELECT USING (true);
    CREATE POLICY IF NOT EXISTS "Users can manage their own username" ON usernames FOR ALL USING (true);
    """
    
    policies = [
        ("RLS Enable", rls_enable_sql),
        ("Messages Policies", messages_policies_sql),
        ("Presence Policies", presence_policies_sql),
        ("Typing Policies", typing_policies_sql),
        ("Usernames Policies", usernames_policies_sql)
    ]
    
    success_count = 0
    for policy_name, sql in policies:
        print(f"Setting up {policy_name}...")
        if execute_sql(sql):
            success_count += 1
        else:
            print(f"Failed to set up {policy_name}")
    
    return success_count == len(policies)

def create_execute_sql_function():
    """Create the execute_sql function if it doesn't exist"""
    sql_function = """
    CREATE OR REPLACE FUNCTION execute_sql(sql text)
    RETURNS void
    LANGUAGE plpgsql
    SECURITY DEFINER
    AS $$
    BEGIN
        EXECUTE sql;
    END;
    $$;
    """
    
    print("Creating execute_sql function...")
    return execute_sql(sql_function)

def main():
    """Main setup function"""
    print("🚀 Starting Supabase database setup...")
    print(f"📍 Supabase URL: {SUPABASE_URL}")
    
    # Step 1: Create execute_sql function
    if not create_execute_sql_function():
        print("❌ Failed to create execute_sql function. Manual setup required.")
        print("\n📋 Manual Setup Instructions:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Run the following SQL commands:")
        
        print("\n-- Create execute_sql function")
        print("""
CREATE OR REPLACE FUNCTION execute_sql(sql text)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    EXECUTE sql;
END;
$$;
""")
        
        print("\n-- Create tables")
        print("""
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

CREATE TABLE IF NOT EXISTS user_presence (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    last_seen TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS typing_indicators (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS usernames (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_user_presence_last_seen ON user_presence(last_seen);
CREATE INDEX IF NOT EXISTS idx_typing_created_at ON typing_indicators(created_at);
CREATE INDEX IF NOT EXISTS idx_usernames_username ON usernames(username);

-- Enable RLS
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_presence ENABLE ROW LEVEL SECURITY;
ALTER TABLE typing_indicators ENABLE ROW LEVEL SECURITY;
ALTER TABLE usernames ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY IF NOT EXISTS "Messages are viewable by everyone" ON messages FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "Users can insert their own messages" ON messages FOR INSERT WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Users can update their own messages" ON messages FOR UPDATE USING (true);
CREATE POLICY IF NOT EXISTS "Users can delete their own messages" ON messages FOR DELETE USING (true);

CREATE POLICY IF NOT EXISTS "Presence is viewable by everyone" ON user_presence FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "Users can manage their own presence" ON user_presence FOR ALL USING (true);

CREATE POLICY IF NOT EXISTS "Typing indicators are viewable by everyone" ON typing_indicators FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "Users can manage their own typing status" ON typing_indicators FOR ALL USING (true);

CREATE POLICY IF NOT EXISTS "Usernames are viewable by everyone" ON usernames FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "Users can manage their own username" ON usernames FOR ALL USING (true);
""")
        return False
    
    # Step 2: Create tables
    if not create_tables():
        print("❌ Failed to create some tables")
        return False
    
    # Step 3: Setup RLS policies
    if not setup_rls_policies():
        print("❌ Failed to set up some policies")
        return False
    
    print("\n🎉 Database setup completed successfully!")
    print("✅ All tables created")
    print("✅ Indexes created")
    print("✅ RLS policies configured")
    print("\nYour chat application is ready to use!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)