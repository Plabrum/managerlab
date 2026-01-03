import { ObjectActions } from '@/components/object-detail';
import { PageTopBar } from '@/components/page-topbar';
import { UserSettingsCard } from '@/components/settings/user-settings-card';
import { useEditAction } from '@/hooks/use-edit-action';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { useUsersCurrentUserGetCurrentUserSuspense } from '@/openapi/users/users';

export function UserSettingsPage() {
  const { data: currentUser, refetch } =
    useUsersCurrentUserGetCurrentUserSuspense();

  // URL parameter-based edit mode with permission checking
  const { isEditMode, openEdit, closeEdit } = useEditAction({
    actions: currentUser.actions || [],
  });

  return (
    <PageTopBar
      title="User Settings"
      actions={
        <ObjectActions
          data={currentUser}
          actionGroup={ActionGroupType.user_actions}
          onRefetch={refetch}
          editMode={{
            isOpen: isEditMode,
            onOpen: openEdit,
            onClose: closeEdit,
          }}
        />
      }
    >
      <UserSettingsCard user={currentUser} />
    </PageTopBar>
  );
}
