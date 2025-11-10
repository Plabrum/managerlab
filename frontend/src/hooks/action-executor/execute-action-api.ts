import type {
  ActionDTO,
  ActionGroupType,
  ActionExecutionResponse,
  ActionsActionGroupExecuteActionBody,
  ActionsActionGroupObjectIdExecuteObjectActionBody,
} from '@/openapi/ariveAPI.schemas';

type ExecuteActionApiParams = {
  action: ActionDTO;
  actionGroup: ActionGroupType;
  objectId?: string;
  actionBody?:
    | ActionsActionGroupExecuteActionBody
    | ActionsActionGroupObjectIdExecuteObjectActionBody;
  executeGroupActionMutation: {
    mutateAsync: (params: {
      actionGroup: ActionGroupType;
      data: ActionsActionGroupExecuteActionBody;
    }) => Promise<ActionExecutionResponse>;
  };
  executeObjectActionMutation: {
    mutateAsync: (params: {
      actionGroup: ActionGroupType;
      objectId: string;
      data: ActionsActionGroupObjectIdExecuteObjectActionBody;
    }) => Promise<ActionExecutionResponse>;
  };
};

/**
 * Execute action API call with proper typing based on whether we have an objectId
 */
export async function executeActionApi({
  action,
  actionGroup,
  objectId,
  actionBody,
  executeGroupActionMutation,
  executeObjectActionMutation,
}: ExecuteActionApiParams): Promise<ActionExecutionResponse> {
  // Use provided action body or build default one
  const requestBody =
    actionBody || ({ action: action.action, data: {} } as const);

  // Execute with proper typing based on whether we have an objectId
  if (objectId) {
    return await executeObjectActionMutation.mutateAsync({
      actionGroup,
      objectId,
      data: requestBody as ActionsActionGroupObjectIdExecuteObjectActionBody,
    });
  } else {
    return await executeGroupActionMutation.mutateAsync({
      actionGroup,
      data: requestBody as ActionsActionGroupExecuteActionBody,
    });
  }
}
