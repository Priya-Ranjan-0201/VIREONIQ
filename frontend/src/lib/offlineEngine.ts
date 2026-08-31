import { openDB } from 'idb';
import api from './axios';

const DB_NAME = 'placeiq-offline';
const DB_VERSION = 1;

export interface OfflineSession {
  id: string;
  role_category: string;
  answers: {
    question_id: string;
    answer_text: string;
    duration_s: number;
    timestamp: string;
  }[];
  completed_at: string;
}

export async function getOfflineDB() {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      if (!db.objectStoreNames.contains('bundles')) {
        db.createObjectStore('bundles', { keyPath: 'role_category' });
      }
      if (!db.objectStoreNames.contains('sessions')) {
        db.createObjectStore('sessions', { keyPath: 'id' });
      }
    },
  });
}

export async function saveOfflineBundle(roleCategory: string, questions: any[]) {
  const db = await getOfflineDB();
  await db.put('bundles', {
    role_category: roleCategory,
    questions,
    downloaded_at: new Date().toISOString(),
  });
}

export async function getOfflineBundle(roleCategory: string) {
  const db = await getOfflineDB();
  return db.get('bundles', roleCategory);
}

export async function queueOfflineSession(session: OfflineSession) {
  const db = await getOfflineDB();
  await db.put('sessions', session);
}

export async function getPendingSessions(): Promise<OfflineSession[]> {
  const db = await getOfflineDB();
  return db.getAll('sessions');
}

export async function deleteOfflineSession(id: string) {
  const db = await getOfflineDB();
  await db.delete('sessions', id);
}

export async function syncOfflineSessions(): Promise<{ success: boolean; syncedCount: number }> {
  try {
    const pending = await getPendingSessions();
    if (pending.length === 0) {
      return { success: true, syncedCount: 0 };
    }

    // Call bulk sync endpoint
    const response = await api.post('/offline/sync', { sessions: pending });
    
    if (response.status === 200 || response.status === 201) {
      for (const sess of pending) {
        await deleteOfflineSession(sess.id);
      }
      return { success: true, syncedCount: pending.length };
    }
    
    return { success: false, syncedCount: 0 };
  } catch (error) {
    console.error('Offline session sync failed:', error);
    return { success: false, syncedCount: 0 };
  }
}
