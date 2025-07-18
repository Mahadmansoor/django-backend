import os
from rest_framework.response import Response
from .models import FolderAccess, FileAccess, User
from django.conf import settings
from django.http import FileResponse, HttpResponseBadRequest, Http404
import zipfile
import io
import shutil
from .serializers import LoginSerializer, BulkFolderAccessSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import is_admin, can_delete_folder, can_rename_folder, can_view_folder


def login_user(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        print('validated data is: ', serializer.validated_data)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        user_data = {
            "username": user.username,
            "role": user.role 
        }
        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_data": user_data
            })
    return Response(serializer.errors)

def logout_user(request):
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token is None:
            return Response({"error": "Refresh token is required"})
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"detail": "Logout successful"})
    except Exception as e:
        return Response({"error": str(e)})

# def get_folders(request):
#     print('inside get folder')
#     user = request.user
#     folders = []
#     db_entries = FolderAccess.objects.filter(user=user)
#     db_has_folders = db_entries.exists()
#     print('db folders: ', db_has_folders)
#     # Check folders on disk (excluding hidden)
#     try:
#         disk_folders = [
#             name for name in os.listdir(settings.MEDIA_ROOT)
#             if os.path.isdir(os.path.join(settings.MEDIA_ROOT, name)) and not name.startswith('.')
#         ]
#     except FileNotFoundError:
#         disk_folders = []

#     disk_has_folders = len(disk_folders) > 0
#     print('disk has folders: ', disk_has_folders)
#     if not db_has_folders and not disk_has_folders:
#         return Response({"message": "No folders found."})
#     if is_admin(user):
#         try:
#             top_level_folders = [
#                 f for f in os.listdir(settings.MEDIA_ROOT)
#                 if os.path.isdir(os.path.join(settings.MEDIA_ROOT, f)) and not f.startswith('.')
#             ]
#         except Exception:
#             top_level_folders = []

#         for folder in top_level_folders:
#             abs_folder_path = os.path.join(settings.MEDIA_ROOT, folder)
#             try:
#                 all_items = os.listdir(abs_folder_path)
#                 subfolders = [
#                     sf for sf in all_items
#                     if os.path.isdir(os.path.join(abs_folder_path, sf)) and not sf.startswith('.')
#                 ]
#             except Exception:
#                 subfolders = []

#             folders.append({
#                 "folder_path": folder,
#                 "can_view": True,
#                 "can_edit": True,
#                 "can_delete": True,
#                 "subfolders": subfolders
#             })

#     else:
#         access_entries = FolderAccess.objects.filter(user=user)

#         if not access_entries.exists():
#             return Response({"error": "You do not have access to any folders."})

#         for entry in access_entries:
#             rel_folder_path = entry.folder_path

#             if not can_view_folder(user, rel_folder_path):
#                 continue  # Just to double-check access

#             abs_folder_path = os.path.join(settings.MEDIA_ROOT, rel_folder_path)
#             try:
#                 all_items = os.listdir(abs_folder_path)
#                 subfolders = [
#                     f for f in all_items
#                     if os.path.isdir(os.path.join(abs_folder_path, f)) and not f.startswith('.')
#                 ]
#             except Exception:
#                 subfolders = []

#             folders.append({
#                 "folder_path": rel_folder_path,
#                 "can_view": True,
#                 "can_edit": can_rename_folder(user, rel_folder_path),
#                 "can_delete": can_delete_folder(user, rel_folder_path),
#                 "subfolders": subfolders
#             })
#     return Response({"folders": folders})


                                            #Following function can be used as a specific access/permission function for a better code structure
                                            #for now I have commented it.


# def get_file_access(request):
#     user = request.user
#     rel_file_path = request.data.get("file_path", "").strip()
#     abs_file_path = os.path.join(settings.MEDIA_ROOT, rel_file_path)

#     if not os.path.isfile(abs_file_path):
#         return Response({"error": f"{rel_file_path} is not a valid file."}, status=400)

#     try:
#         access = FileAccess.objects.get(user=user, file_path=rel_file_path, can_view=True)
#     except FileAccess.DoesNotExist:
#         return Response({"error": "You do not have permission to view this file."}, status=403)

#     return Response({
#         "file_path": rel_file_path,
#         "can_view": access.can_view,
#         "can_edit": access.can_edit,
#         "can_delete": access.can_delete,
#         "file_url": f"/{rel_file_path}"
#     })



# def get_files(request):
#     user = request.user
#     rel_folder_path = request.data.get("folder_path", "").strip()
#     abs_folder_path = os.path.join(settings.MEDIA_ROOT, rel_folder_path)

#     if not rel_folder_path or not os.path.isdir(abs_folder_path):
#         return Response({"error": "Invalid folder path."})

#     # === List Files ===
#     all_files = [
#         f for f in os.listdir(abs_folder_path)
#         if os.path.isfile(os.path.join(abs_folder_path, f))
#     ]
#     file_paths = [os.path.join(rel_folder_path, f) for f in all_files]
#     access_records = FileAccess.objects.filter(user=user, file_path__in=file_paths)
#     access_map = {record.file_path: record for record in access_records}

#     accessible_files = []
#     if is_admin(user):
#          for file_name in all_files:
#             rel_file_path = os.path.join(rel_folder_path, file_name)
#             file_url = f"{settings.MEDIA_URL}{rel_file_path}"
#             download_url = request.build_absolute_uri(f"/media/{rel_file_path}")
#             accessible_files.append({
#                 "file_name": file_name,
#                 "can_view": True,
#                 "can_edit": True,
#                 "can_delete": True,
#                 "file_url": file_url,
#                 "download_url": download_url
#             })
#     else:
#         for file_name in all_files:
#             rel_file_path = os.path.join(rel_folder_path, file_name)
#             access = access_map.get(rel_file_path)

#             if access and access.can_view:
#                 file_url = f"{settings.MEDIA_URL}{rel_file_path}"
#                 download_url = request.build_absolute_uri(f"/media/{rel_file_path}")
#                 accessible_files.append({
#                     "file_name": file_name,
#                     "can_view": access.can_view,
#                     "can_edit": access.can_edit,
#                     "can_delete": access.can_delete,
#                     "file_url": file_url,
#                     "download_url": download_url
#                 })

#         # === List Folders ===
#         all_folders = [
#             d for d in os.listdir(abs_folder_path)
#             if os.path.isdir(os.path.join(abs_folder_path, d))
#         ]

#         # Full paths like test_folder_1/subfolder_name
#         full_folder_paths = [os.path.join(rel_folder_path, d) for d in all_folders]

#         # Fetch permissions for those folders
#         folder_access_records = FolderAccess.objects.filter(
#             user=user,
#             folder_path__in=full_folder_paths,
#             can_view=True
#         )

#         # Build a map for quick lookup
#         folder_access_map = {f.folder_path: f for f in folder_access_records}

#         # Prepare folder list with permissions
#         accessible_folders = []
#         for folder_name in all_folders:
#             folder_rel_path = os.path.join(rel_folder_path, folder_name)
#             access = folder_access_map.get(folder_rel_path)
#             if access:
#                 accessible_folders.append({
#                     "name": folder_name,
#                     "path": folder_rel_path,
#                     "can_view": access.can_view,
#                     "can_edit": access.can_edit,
#                     "can_delete": access.can_delete
#                 })

#         # === Final Response ===
#         return Response({
#             "folder_path": rel_folder_path,
#             "files": accessible_files,
#             "folders": accessible_folders
#         })


def get_files(request):
    user = request.user
    rel_folder_path = request.data.get("folder_path", "").strip()
    abs_folder_path = os.path.join(settings.MEDIA_ROOT, rel_folder_path)

    if not rel_folder_path or not os.path.isdir(abs_folder_path):
        return Response({"error": "Invalid folder path."})

    # === List Files ===
    all_files = [
        f for f in os.listdir(abs_folder_path)
        if os.path.isfile(os.path.join(abs_folder_path, f))
    ]
    file_paths = [os.path.join(rel_folder_path, f) for f in all_files]

    accessible_files = []

    if is_admin(user):
        # Admin sees all files with full permissions
        for file_name in all_files:
            rel_file_path = os.path.join(rel_folder_path, file_name)
            file_url = f"{settings.MEDIA_URL}{rel_file_path}"
            download_url = request.build_absolute_uri(f"/media/{rel_file_path}")
            accessible_files.append({
                "file_name": file_name,
                "can_view": True,
                "can_edit": True,
                "can_delete": True,
                "file_url": file_url,
                "download_url": download_url
            })
    else:
        access_records = FileAccess.objects.filter(user=user, file_path__in=file_paths)
        access_map = {record.file_path: record for record in access_records}

        for file_name in all_files:
            rel_file_path = os.path.join(rel_folder_path, file_name)
            access = access_map.get(rel_file_path)

            if access and access.can_view:
                file_url = f"{settings.MEDIA_URL}{rel_file_path}"
                download_url = request.build_absolute_uri(f"/media/{rel_file_path}")
                accessible_files.append({
                    "file_name": file_name,
                    "can_view": access.can_view,
                    "can_edit": access.can_edit,
                    "can_delete": access.can_delete,
                    "file_url": file_url,
                    "download_url": download_url
                })

    # === List Folders ===
    all_folders = [
        d for d in os.listdir(abs_folder_path)
        if os.path.isdir(os.path.join(abs_folder_path, d))
    ]

    full_folder_paths = [os.path.join(rel_folder_path, d) for d in all_folders]

    accessible_folders = []

    if is_admin(user):
        # Admin sees all subfolders with full permissions
        for folder_name in all_folders:
            folder_rel_path = os.path.join(rel_folder_path, folder_name)
            accessible_folders.append({
                "name": folder_name,
                "path": folder_rel_path,
                "can_view": True,
                "can_edit": True,
                "can_delete": True
            })
    else:
        folder_access_records = FolderAccess.objects.filter(
            user=user,
            folder_path__in=full_folder_paths,
            can_view=True
        )
        folder_access_map = {f.folder_path: f for f in folder_access_records}

        for folder_name in all_folders:
            folder_rel_path = os.path.join(rel_folder_path, folder_name)
            access = folder_access_map.get(folder_rel_path)
            if access:
                accessible_folders.append({
                    "name": folder_name,
                    "path": folder_rel_path,
                    "can_view": access.can_view,
                    "can_edit": access.can_edit,
                    "can_delete": access.can_delete
                })

    return Response({
        "folder_path": rel_folder_path,
        "files": accessible_files,
        "folders": accessible_folders
    })


def download(request):
    folder_path = request.data.get("folder_path")
    if not folder_path:
        return Response({"error": "No folder path provided"}, status=400)

    abs_folder_path = os.path.join(settings.MEDIA_ROOT, folder_path)
    # if not os.path.exists(abs_folder_path) or not os.path.isdir(abs_folder_path):
    #     raise Http404("Folder not found")
    if not FolderAccess.objects.filter(folder_path=folder_path, user=request.user).exists():
        raise Http404("Folder not found in database")

    # Create zip in memory
    zip_stream = io.BytesIO()
    with zipfile.ZipFile(zip_stream, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(abs_folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, abs_folder_path)
                zipf.write(file_path, arcname)

    zip_stream.seek(0)
    folder_name = os.path.basename(abs_folder_path)
    response = FileResponse(zip_stream, as_attachment=True, filename=f"{folder_name}.zip")
    return response

def rename(request):
    old_path = request.data.get('old_path')
    new_name = request.data.get('new_name')

    if not old_path or not new_name:
        return Response({"error": "Missing old_path or new_name"})

    # Strip '/media/' only if present in the path
    # if old_path.startswith('/media/'):
    #     relative_path = old_path[len('/media/'):]  # remove '/media/'
    # else:
    #     relative_path = old_path  # assume already relative
    relative_path = old_path
    abs_old_path = os.path.join(settings.MEDIA_ROOT, relative_path)
    dir_name = os.path.dirname(abs_old_path)
    abs_new_path = os.path.join(dir_name, new_name)

    if not os.path.exists(abs_old_path):
        return Response({"error": f"Item does not exist at: {abs_old_path}"})

    try:
        os.rename(abs_old_path, abs_new_path)
    except Exception as e:
        return Response({"error": str(e)})

    rel_new_path = os.path.join(os.path.dirname(relative_path), new_name)

    if os.path.isdir(abs_new_path):
        FolderAccess.objects.filter(folder_path=relative_path).update(folder_path=rel_new_path)
    else:
        FileAccess.objects.filter(file_path=relative_path).update(file_path=rel_new_path)

    return Response({"message": "Renamed successfully", "new_path": rel_new_path})


def delete_file_folder(request):
    path = request.data.get('path')

    if not path:
        return Response({"error": "Missing path"}, status=400)

    # Convert /media/... to relative path
    relative_path = path.replace('/media/', '')
    abs_path = os.path.join(settings.MEDIA_ROOT, relative_path)

    if not os.path.exists(abs_path):
        return Response({"error": "Path does not exist"})

    try:
        if os.path.isdir(abs_path):
            shutil.rmtree(abs_path)
            FolderAccess.objects.filter(folder_path=relative_path).delete()
        else:
            os.remove(abs_path)
            FileAccess.objects.filter(file_path=relative_path).delete()
    except Exception as e:
        return Response({"error": str(e)})

    return Response({"message": "Deleted successfully"})


def create_folder(request):
    name = request.data.get('name')
    path = request.data.get('path') or '.'
    clean_path = os.path.join(path, name)
    if clean_path.startswith('./'):
        clean_path = clean_path[2:]

    abs_parent_path = os.path.join(settings.MEDIA_ROOT, path)
    abs_new_path = os.path.join(abs_parent_path, name)

    if FolderAccess.objects.filter(folder_path=clean_path).exists():
        return Response({"error": "Folder already exists in database"}, status=400)

    if os.path.exists(abs_new_path):
        print("Folder exists on disk but not in DB. Re-using it.")

    try:
        os.makedirs(abs_new_path, exist_ok=True)

        # Register in DB
        FolderAccess.objects.create(
            folder_path=clean_path,
            user=request.user,
            can_view=True,
            can_edit=False,
            can_delete=False
        )
        return Response({"message": "Folder created successfully"})

    except Exception as e:
        return Response({"error": str(e)})


    

def create_file(request):
    print('inside create file')

    uploaded_file = request.FILES.get('file')
    upload_path = request.POST.get('path') or ''  # Handle None or ''

    print('uploaded file:', uploaded_file)
    print('uploaded path:', upload_path)

    if not uploaded_file:
        return Response({"error": "Missing file"}, status=400)

    # Handle empty path case
    if upload_path.strip() == '':
        dest_dir = settings.MEDIA_ROOT  # Save to base directory
        db_path = uploaded_file.name  # Save only file name in DB path
    else:
        dest_dir = os.path.join(settings.MEDIA_ROOT, upload_path)
        db_path = os.path.join(upload_path, uploaded_file.name)

    # Make sure destination folder exists
    os.makedirs(dest_dir, exist_ok=True)

    # Save file to destination path
    dest_path = os.path.join(dest_dir, uploaded_file.name)
    with open(dest_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    print('db_path is: ', db_path)
    print('before saving file to db')
    FileAccess.objects.create(
        file_path=db_path,
        user=request.user,
        can_view=True,
        can_edit=True,
        can_delete=True
    )
    print('saved')

    return Response({"message": "File uploaded successfully"})


def upload_fol(request):
    print('inside folder')

    uploaded_files = request.FILES.getlist('files')
    relative_paths = request.POST.getlist('paths')
    base_path = request.POST.get('base_path', '').strip()
    print('relative paths: ', relative_paths)
    print('base path: ', base_path)
    folder_paths_set = set()

    for i, file in enumerate(uploaded_files):
        print('inside for loop')
        rel_path = relative_paths[i] if i < len(relative_paths) else file.name
        full_path = os.path.join(base_path, rel_path)
        abs_path = os.path.join(settings.MEDIA_ROOT, full_path)
        print('full path is: ', full_path)
        print('abs path: ', abs_path)
        print('→ Saving to:', full_path)

        # Create parent folders
        parent_folder_path = os.path.dirname(full_path)
        print('parent folder: ', parent_folder_path)
        while parent_folder_path and parent_folder_path not in folder_paths_set:
            abs_folder = os.path.join(settings.MEDIA_ROOT, parent_folder_path)
            os.makedirs(abs_folder, exist_ok=True)
            folder_paths_set.add(parent_folder_path)

            FolderAccess.objects.get_or_create(
                folder_path=parent_folder_path,
                defaults={
                    'user': request.user,
                    'can_view': True,
                    'can_edit': True,
                    'can_delete': True
                }
            )
            parent_folder_path = os.path.dirname(parent_folder_path)

        # Save file
        with open(abs_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        FileAccess.objects.create(
            file_path=full_path,
            user=request.user,
            can_view=True,
            can_edit=True,
            can_delete=True
        )

    return Response({"message": "Folder uploaded successfully"})


def users(request):
    if request.user.role == 'admin' or request.user.role == 'Admin':
        users = User.objects.all().values('username')
        return Response({"users": users})
    else:
        return Response({"Error":"User is not admin"})
    

def folders(request):
    folders = FolderAccess.objects.values_list('folder_path', flat=True).distinct()
    return Response({
        "folders": [{"folder_path": path} for path in folders]
    })


def folder_access(request):
    print('inside folder access middleware')

    for item in request.data:
        usernames = item.get("username", [])
        folder_paths = item.get("folder_path", [])
        can_view = item.get("can_view", True)
        can_edit = item.get("can_edit", False)
        can_delete = item.get("can_delete", False)

    print('after for loop')

    if isinstance(usernames, str):
        usernames = [usernames]
    if isinstance(folder_paths, str):
        folder_paths = [folder_paths]

    print('validating users, folders')
    if not User.objects.filter(username__in=usernames).exists():
        print('if not user')
        return Response({"error": "One or more users do not exist."})
    if not folder_paths:
        print('if not folder')
        return Response({"error": "No folder paths provided."})

    print('after validation')
    updated_objs = []

    for username in usernames:
        user = User.objects.get(username=username)
        print('user: ', user)

        for folder_path in folder_paths:
            print('folder_path: ', folder_path)

            # Assign folder-level access
            obj, created = FolderAccess.objects.get_or_create(
                user=user,
                folder_path=folder_path,
                defaults={
                    'can_view': can_view,
                    'can_edit': can_edit,
                    'can_delete': can_delete,
                }
            )
            if not created:
                obj.can_view = can_view
                obj.can_edit = can_edit
                obj.can_delete = can_delete
            updated_objs.append(obj)

            # Grant access to files/subfolders within the folder
            full_folder_path = os.path.join(settings.MEDIA_ROOT, folder_path)
            if os.path.exists(full_folder_path):
                for item in os.listdir(full_folder_path):
                    if not item.startswith('.'):  # skip hidden
                        item_path = os.path.join(folder_path, item)  # relative path
                        FileAccess.objects.update_or_create(
                            user=user,
                            file_path=item_path,
                            defaults={
                                "can_view": can_view,
                                "can_edit": can_edit,
                                "can_delete": can_delete
                            }
                        )

    # Save updated folder access records
    if len(updated_objs) == 1:
        updated_objs[0].save()
    elif len(updated_objs) > 1:
        FolderAccess.objects.bulk_update(updated_objs, ['can_view', 'can_edit', 'can_delete'])

    return Response({"message": f"Permissions assigned to {len(updated_objs)} folder records, and their files."})