import os.path
# Impor library untuk waktu
from datetime import datetime, timezone, timedelta 

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
# GANTI INI dengan ID dari skrip pertama
COURSE_ID_TO_USE = "820146648448" 

def create_assignment(creds, title, description, scheduledTime=None, due_date=None, due_time=None, state='DRAFT'):
    """
    Membuat tugas baru untuk dijadwalkan WIB.
    """
    try:
        service = build("classroom", "v1", credentials=creds)

        # === 1. GET COURSE (Mengambil data kursus) ===
        print(f"Mengambil data untuk Course ID: {COURSE_ID_TO_USE}...")
        course_info = service.courses().get(id=COURSE_ID_TO_USE).execute()
        print(f"Nama Kursus: {course_info.get('name')}")
        print(f"Status Kursus: {course_info.get('courseState')}")

        if course_info.get('courseState') != 'ACTIVE':
            print("\nPERINGATAN: Kursus ini belum 'ACTIVE'.")
            print("Anda harus menekan 'Accept' di Google Classroom sebelum bisa menambah tugas.")
            return 

        # === 2. CREATE ASSIGNMENT (Membuat tugas baru) ===
        print("\nMembuat tugas baru untuk dijadwalkan...")
        
        # --- Penjadwalan Waktu ---
        # Tentukan zona waktu WIB (UTC+7)
        if scheduledTime is not None:
            zona_waktu_wib = timezone(timedelta(hours=7))
        # Buat waktu 6:55 WIB hari ini (Tahun, Bulan, Hari, Jam, Menit, Zona Waktu)
            waktu_jadwal_wib = datetime(scheduledTime['Tahun'], scheduledTime['Bulan'], scheduledTime['Hari'], scheduledTime['Jam'], scheduledTime['Menit'], tzinfo=zona_waktu_wib)
            
            # Konversi ke UTC dan format ke string ISO (RFC3339)
            # Ini akan menghasilkan sesuatu seperti: '2025-10-27T23:55:00+00:00'
            waktu_jadwal_utc_str = waktu_jadwal_wib.astimezone(timezone.utc).isoformat()
        
            print(f"Tugas akan dijadwalkan untuk: {waktu_jadwal_wib} (WIB)")
            print(f"String UTC yang dikirim ke API: {waktu_jadwal_utc_str}")
        
        # Tentukan due date (jika masih diperlukan)
        due_date_obj = { 'year': 2025, 'month': 12, 'day': 30 }
        due_time_obj = { 'hours': 16, 'minutes': 59 } # 16:00 UTC (23:00 WIB)
        due_date_obj = due_date if due_date else due_date_obj
        due_time_obj = due_time if due_time else due_time_obj
        
        assignment_body = {
            'title': title,
            'description': description,
            'workType': 'ASSIGNMENT',
            
            # PENTING: Ubah state ke DRAFT
            'state': state,
            
            # PENTING: Tambahkan scheduleTime
            'scheduledTime': waktu_jadwal_utc_str if scheduledTime else None,
            
            'maxPoints': 100,
            'dueDate': due_date_obj,
            'dueTime': due_time_obj
        }

        new_assignment = service.courses().courseWork().create(
            courseId=COURSE_ID_TO_USE,
            body=assignment_body
        ).execute()

        print(f"\nBerhasil membuat draf tugas: {new_assignment.get('title')}")


    except HttpError as error:
        print(f"An error occurred: {error}")
        if error.resp.status == 403:
            print("Error 403: Permission denied.")
            print("Apakah Anda yakin sudah 'Accept' undangan mengajar di UI Google Classroom?")
        elif error.resp.status == 404:
            print("Error 404: Not Found.")
            print(f"Kursus dengan ID '{COURSE_ID_TO_USE}' tidak ditemukan.")

