import logging
import os
import json

import azure.functions as func
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient

import pymsteams

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    alert = req.get_json()
    alertData = alert['data']

    targetResourceType = alertData['context']['resourceType']
    if targetResourceType == 'Microsoft.Compute/virtualMachines':
        logging.warn("Alert for Virtual Machines, Stop the VM !")
        
        rg = alertData['context']['resourceGroupName']
        vm = alertData['context']['resourceName']
        logging.warn('Alert for VM %s', vm)

        credentials, subscription_id = get_credentials()
        compute_client = ComputeManagementClient(credentials, subscription_id)

        async_vm_stop = compute_client.virtual_machines.power_off(rg, vm)
        async_vm_stop.wait()
    else:
        logging.warn("Alert for other types - %s", targetResourceType)
    
    teamsWebHook = os.environ['TeamsWebHook']

    teamsMsg = pymsteams.connectorcard(teamsWebHook)
    teamsMsg.title("Alert Fired !")

    teamsSection = pymsteams.cardsection()
    teamsSection.addFact('Timestamp:', alertData['context']['timestamp'])
    teamsSection.addFact('Severity:', alertData['context']['severity'])
    teamsSection.addFact('Resource:', alertData['context']['resourceGroupName'] + \
                                            ' - ' + alertData['context']['resourceName'])
    teamsSection.addFact('ResourceType:', alertData['context']['resourceType'])
    for metric in alertData['context']['condition']['allOf']:
        teamsSection.addFact('MetricName:', metric['metricName'])
        teamsSection.addFact('MetricValue:', metric['metricValue'])

    teamsMsg.addSection(teamsSection)
    teamsMsg.text("Please take action !")
    teamsMsg.send()

    return func.HttpResponse("Azure Function executed & Alert Msg Sent to Teams !")

def get_credentials():
    subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
    credentials = ServicePrincipalCredentials(
        client_id=os.environ['AZURE_CLIENT_ID'],
        secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant=os.environ['AZURE_TENANT_ID']
    )
    return credentials, subscription_id