# List knowledge base documents

GET https://api.elevenlabs.io/v1/convai/knowledge-base

Get a list of available knowledge base documents

Reference: https://elevenlabs.io/docs/api-reference/knowledge-base/list

## OpenAPI Specification

```yaml
openapi: 3.1.1
info:
  title: Get Knowledge Base List
  version: endpoint_conversationalAi/knowledgeBase.list
paths:
  /v1/convai/knowledge-base:
    get:
      operationId: list
      summary: Get Knowledge Base List
      description: Get a list of available knowledge base documents
      tags:
        - - subpackage_conversationalAi
          - subpackage_conversationalAi/knowledgeBase
      parameters:
        - name: page_size
          in: query
          description: >-
            How many documents to return at maximum. Can not exceed 100,
            defaults to 30.
          required: false
          schema:
            type: integer
        - name: search
          in: query
          description: >-
            If specified, the endpoint returns only such knowledge base
            documents whose names start with this string.
          required: false
          schema:
            type:
              - string
              - 'null'
        - name: show_only_owned_documents
          in: query
          description: >-
            If set to true, the endpoint will return only documents owned by you
            (and not shared from somebody else).
          required: false
          schema:
            type: boolean
        - name: types
          in: query
          description: >-
            If present, the endpoint will return only documents of the given
            types.
          required: false
          schema:
            type:
              - array
              - 'null'
            items:
              $ref: '#/components/schemas/KnowledgeBaseDocumentType'
        - name: sort_direction
          in: query
          description: The direction to sort the results
          required: false
          schema:
            $ref: '#/components/schemas/SortDirection'
        - name: sort_by
          in: query
          description: The field to sort the results by
          required: false
          schema:
            oneOf:
              - $ref: '#/components/schemas/KnowledgeBaseSortBy'
              - type: 'null'
        - name: use_typesense
          in: query
          description: >-
            If set to true, the endpoint will use typesense DB to search for the
            documents).
          required: false
          schema:
            type: boolean
        - name: cursor
          in: query
          description: Used for fetching next page. Cursor is returned in the response.
          required: false
          schema:
            type:
              - string
              - 'null'
        - name: xi-api-key
          in: header
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GetKnowledgeBaseListResponseModel'
        '422':
          description: Validation Error
          content: {}
components:
  schemas:
    KnowledgeBaseDocumentType:
      type: string
      enum:
        - value: file
        - value: url
        - value: text
    SortDirection:
      type: string
      enum:
        - value: asc
        - value: desc
    KnowledgeBaseSortBy:
      type: string
      enum:
        - value: name
        - value: created_at
        - value: updated_at
        - value: size
    KnowledgeBaseDocumentMetadataResponseModel:
      type: object
      properties:
        created_at_unix_secs:
          type: integer
        last_updated_at_unix_secs:
          type: integer
        size_bytes:
          type: integer
      required:
        - created_at_unix_secs
        - last_updated_at_unix_secs
        - size_bytes
    DocumentUsageModeEnum:
      type: string
      enum:
        - value: prompt
        - value: auto
    ResourceAccessInfoRole:
      type: string
      enum:
        - value: admin
        - value: editor
        - value: commenter
        - value: viewer
    ResourceAccessInfo:
      type: object
      properties:
        is_creator:
          type: boolean
        creator_name:
          type: string
        creator_email:
          type: string
        role:
          $ref: '#/components/schemas/ResourceAccessInfoRole'
      required:
        - is_creator
        - creator_name
        - creator_email
        - role
    DependentAvailableAgentIdentifierAccessLevel:
      type: string
      enum:
        - value: admin
        - value: editor
        - value: commenter
        - value: viewer
    DependentAvailableAgentIdentifier:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        type:
          type: string
          enum:
            - type: stringLiteral
              value: available
        created_at_unix_secs:
          type: integer
        access_level:
          $ref: '#/components/schemas/DependentAvailableAgentIdentifierAccessLevel'
      required:
        - id
        - name
        - created_at_unix_secs
        - access_level
    DependentUnknownAgentIdentifier:
      type: object
      properties:
        type:
          type: string
          enum:
            - type: stringLiteral
              value: unknown
    GetKnowledgeBaseSummaryUrlResponseModelDependentAgentsItems:
      oneOf:
        - $ref: '#/components/schemas/DependentAvailableAgentIdentifier'
        - $ref: '#/components/schemas/DependentUnknownAgentIdentifier'
    GetKnowledgeBaseSummaryURLResponseModel:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        metadata:
          $ref: '#/components/schemas/KnowledgeBaseDocumentMetadataResponseModel'
        supported_usages:
          type: array
          items:
            $ref: '#/components/schemas/DocumentUsageModeEnum'
        access_info:
          $ref: '#/components/schemas/ResourceAccessInfo'
        dependent_agents:
          type: array
          items:
            $ref: >-
              #/components/schemas/GetKnowledgeBaseSummaryUrlResponseModelDependentAgentsItems
        type:
          type: string
          enum:
            - type: stringLiteral
              value: url
        url:
          type: string
      required:
        - id
        - name
        - metadata
        - supported_usages
        - access_info
        - dependent_agents
        - type
        - url
    GetKnowledgeBaseSummaryFileResponseModelDependentAgentsItems:
      oneOf:
        - $ref: '#/components/schemas/DependentAvailableAgentIdentifier'
        - $ref: '#/components/schemas/DependentUnknownAgentIdentifier'
    GetKnowledgeBaseSummaryFileResponseModel:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        metadata:
          $ref: '#/components/schemas/KnowledgeBaseDocumentMetadataResponseModel'
        supported_usages:
          type: array
          items:
            $ref: '#/components/schemas/DocumentUsageModeEnum'
        access_info:
          $ref: '#/components/schemas/ResourceAccessInfo'
        dependent_agents:
          type: array
          items:
            $ref: >-
              #/components/schemas/GetKnowledgeBaseSummaryFileResponseModelDependentAgentsItems
        type:
          type: string
          enum:
            - type: stringLiteral
              value: file
      required:
        - id
        - name
        - metadata
        - supported_usages
        - access_info
        - dependent_agents
        - type
    GetKnowledgeBaseSummaryTextResponseModelDependentAgentsItems:
      oneOf:
        - $ref: '#/components/schemas/DependentAvailableAgentIdentifier'
        - $ref: '#/components/schemas/DependentUnknownAgentIdentifier'
    GetKnowledgeBaseSummaryTextResponseModel:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        metadata:
          $ref: '#/components/schemas/KnowledgeBaseDocumentMetadataResponseModel'
        supported_usages:
          type: array
          items:
            $ref: '#/components/schemas/DocumentUsageModeEnum'
        access_info:
          $ref: '#/components/schemas/ResourceAccessInfo'
        dependent_agents:
          type: array
          items:
            $ref: >-
              #/components/schemas/GetKnowledgeBaseSummaryTextResponseModelDependentAgentsItems
        type:
          type: string
          enum:
            - type: stringLiteral
              value: text
      required:
        - id
        - name
        - metadata
        - supported_usages
        - access_info
        - dependent_agents
        - type
    GetKnowledgeBaseListResponseModelDocumentsItems:
      oneOf:
        - $ref: '#/components/schemas/GetKnowledgeBaseSummaryURLResponseModel'
        - $ref: '#/components/schemas/GetKnowledgeBaseSummaryFileResponseModel'
        - $ref: '#/components/schemas/GetKnowledgeBaseSummaryTextResponseModel'
    GetKnowledgeBaseListResponseModel:
      type: object
      properties:
        documents:
          type: array
          items:
            $ref: >-
              #/components/schemas/GetKnowledgeBaseListResponseModelDocumentsItems
        next_cursor:
          type:
            - string
            - 'null'
        has_more:
          type: boolean
      required:
        - documents
        - has_more

```

## SDK Code Examples

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

async function main() {
    const client = new ElevenLabsClient({
        environment: "https://api.elevenlabs.io",
    });
    await client.conversationalAi.knowledgeBase.list({});
}
main();

```

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(
    base_url="https://api.elevenlabs.io"
)

client.conversational_ai.knowledge_base.list()

```

```go
package main

import (
	"fmt"
	"net/http"
	"io"
)

func main() {

	url := "https://api.elevenlabs.io/v1/convai/knowledge-base"

	req, _ := http.NewRequest("GET", url, nil)

	req.Header.Add("xi-api-key", "xi-api-key")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```ruby
require 'uri'
require 'net/http'

url = URI("https://api.elevenlabs.io/v1/convai/knowledge-base")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Get.new(url)
request["xi-api-key"] = 'xi-api-key'

response = http.request(request)
puts response.read_body
```

```java
HttpResponse<String> response = Unirest.get("https://api.elevenlabs.io/v1/convai/knowledge-base")
  .header("xi-api-key", "xi-api-key")
  .asString();
```

```php
<?php

$client = new \GuzzleHttp\Client();

$response = $client->request('GET', 'https://api.elevenlabs.io/v1/convai/knowledge-base', [
  'headers' => [
    'xi-api-key' => 'xi-api-key',
  ],
]);

echo $response->getBody();
```

```csharp
var client = new RestClient("https://api.elevenlabs.io/v1/convai/knowledge-base");
var request = new RestRequest(Method.GET);
request.AddHeader("xi-api-key", "xi-api-key");
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = ["xi-api-key": "xi-api-key"]

let request = NSMutableURLRequest(url: NSURL(string: "https://api.elevenlabs.io/v1/convai/knowledge-base")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "GET"
request.allHTTPHeaderFields = headers

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```









# Delete knowledge base document

DELETE https://api.elevenlabs.io/v1/convai/knowledge-base/{documentation_id}

Delete a document from the knowledge base

Reference: https://elevenlabs.io/docs/api-reference/knowledge-base/delete

## OpenAPI Specification

```yaml
openapi: 3.1.1
info:
  title: Delete Knowledge Base Document
  version: endpoint_conversationalAi/knowledgeBase/documents.delete
paths:
  /v1/convai/knowledge-base/{documentation_id}:
    delete:
      operationId: delete
      summary: Delete Knowledge Base Document
      description: Delete a document from the knowledge base
      tags:
        - - subpackage_conversationalAi
          - subpackage_conversationalAi/knowledgeBase
          - subpackage_conversationalAi/knowledgeBase/documents
      parameters:
        - name: documentation_id
          in: path
          description: >-
            The id of a document from the knowledge base. This is returned on
            document addition.
          required: true
          schema:
            type: string
        - name: force
          in: query
          description: >-
            If set to true, the document will be deleted regardless of whether
            it is used by any agents and it will be deleted from the dependent
            agents.
          required: false
          schema:
            type: boolean
        - name: xi-api-key
          in: header
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                description: Any type
        '422':
          description: Validation Error
          content: {}

```

## SDK Code Examples

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

async function main() {
    const client = new ElevenLabsClient({
        environment: "https://api.elevenlabs.io",
    });
    await client.conversationalAi.knowledgeBase.documents.delete("documentation_id", {});
}
main();

```

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(
    base_url="https://api.elevenlabs.io"
)

client.conversational_ai.knowledge_base.documents.delete(
    documentation_id="documentation_id"
)

```

```go
package main

import (
	"fmt"
	"net/http"
	"io"
)

func main() {

	url := "https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id"

	req, _ := http.NewRequest("DELETE", url, nil)

	req.Header.Add("xi-api-key", "xi-api-key")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```ruby
require 'uri'
require 'net/http'

url = URI("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Delete.new(url)
request["xi-api-key"] = 'xi-api-key'

response = http.request(request)
puts response.read_body
```

```java
HttpResponse<String> response = Unirest.delete("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id")
  .header("xi-api-key", "xi-api-key")
  .asString();
```

```php
<?php

$client = new \GuzzleHttp\Client();

$response = $client->request('DELETE', 'https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id', [
  'headers' => [
    'xi-api-key' => 'xi-api-key',
  ],
]);

echo $response->getBody();
```

```csharp
var client = new RestClient("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id");
var request = new RestRequest(Method.DELETE);
request.AddHeader("xi-api-key", "xi-api-key");
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = ["xi-api-key": "xi-api-key"]

let request = NSMutableURLRequest(url: NSURL(string: "https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "DELETE"
request.allHTTPHeaderFields = headers

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```
# Get knowledge base document

GET https://api.elevenlabs.io/v1/convai/knowledge-base/{documentation_id}

Get details about a specific documentation making up the agent's knowledge base

Reference: https://elevenlabs.io/docs/api-reference/knowledge-base/get-document

## OpenAPI Specification

```yaml
openapi: 3.1.1
info:
  title: Get Documentation From Knowledge Base
  version: endpoint_conversationalAi/knowledgeBase/documents.get
paths:
  /v1/convai/knowledge-base/{documentation_id}:
    get:
      operationId: get
      summary: Get Documentation From Knowledge Base
      description: >-
        Get details about a specific documentation making up the agent's
        knowledge base
      tags:
        - - subpackage_conversationalAi
          - subpackage_conversationalAi/knowledgeBase
          - subpackage_conversationalAi/knowledgeBase/documents
      parameters:
        - name: documentation_id
          in: path
          description: >-
            The id of a document from the knowledge base. This is returned on
            document addition.
          required: true
          schema:
            type: string
        - name: agent_id
          in: query
          required: false
          schema:
            type: string
        - name: xi-api-key
          in: header
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: >-
                  #/components/schemas/conversational_ai_knowledge_base_documents_get_Response_200
        '422':
          description: Validation Error
          content: {}
components:
  schemas:
    KnowledgeBaseDocumentMetadataResponseModel:
      type: object
      properties:
        created_at_unix_secs:
          type: integer
        last_updated_at_unix_secs:
          type: integer
        size_bytes:
          type: integer
      required:
        - created_at_unix_secs
        - last_updated_at_unix_secs
        - size_bytes
    DocumentUsageModeEnum:
      type: string
      enum:
        - value: prompt
        - value: auto
    ResourceAccessInfoRole:
      type: string
      enum:
        - value: admin
        - value: editor
        - value: commenter
        - value: viewer
    ResourceAccessInfo:
      type: object
      properties:
        is_creator:
          type: boolean
        creator_name:
          type: string
        creator_email:
          type: string
        role:
          $ref: '#/components/schemas/ResourceAccessInfoRole'
      required:
        - is_creator
        - creator_name
        - creator_email
        - role
    GetKnowledgeBaseURLResponseModel:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        metadata:
          $ref: '#/components/schemas/KnowledgeBaseDocumentMetadataResponseModel'
        supported_usages:
          type: array
          items:
            $ref: '#/components/schemas/DocumentUsageModeEnum'
        access_info:
          $ref: '#/components/schemas/ResourceAccessInfo'
        extracted_inner_html:
          type: string
        type:
          type: string
          enum:
            - type: stringLiteral
              value: url
        url:
          type: string
      required:
        - id
        - name
        - metadata
        - supported_usages
        - access_info
        - extracted_inner_html
        - type
        - url
    GetKnowledgeBaseFileResponseModel:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        metadata:
          $ref: '#/components/schemas/KnowledgeBaseDocumentMetadataResponseModel'
        supported_usages:
          type: array
          items:
            $ref: '#/components/schemas/DocumentUsageModeEnum'
        access_info:
          $ref: '#/components/schemas/ResourceAccessInfo'
        extracted_inner_html:
          type: string
        type:
          type: string
          enum:
            - type: stringLiteral
              value: file
      required:
        - id
        - name
        - metadata
        - supported_usages
        - access_info
        - extracted_inner_html
        - type
    GetKnowledgeBaseTextResponseModel:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        metadata:
          $ref: '#/components/schemas/KnowledgeBaseDocumentMetadataResponseModel'
        supported_usages:
          type: array
          items:
            $ref: '#/components/schemas/DocumentUsageModeEnum'
        access_info:
          $ref: '#/components/schemas/ResourceAccessInfo'
        extracted_inner_html:
          type: string
        type:
          type: string
          enum:
            - type: stringLiteral
              value: text
      required:
        - id
        - name
        - metadata
        - supported_usages
        - access_info
        - extracted_inner_html
        - type
    conversational_ai_knowledge_base_documents_get_Response_200:
      oneOf:
        - $ref: '#/components/schemas/GetKnowledgeBaseURLResponseModel'
        - $ref: '#/components/schemas/GetKnowledgeBaseFileResponseModel'
        - $ref: '#/components/schemas/GetKnowledgeBaseTextResponseModel'

```

## SDK Code Examples

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

async function main() {
    const client = new ElevenLabsClient({
        environment: "https://api.elevenlabs.io",
    });
    await client.conversationalAi.knowledgeBase.documents.get("documentation_id", {});
}
main();

```

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(
    base_url="https://api.elevenlabs.io"
)

client.conversational_ai.knowledge_base.documents.get(
    documentation_id="documentation_id"
)

```

```go
package main

import (
	"fmt"
	"net/http"
	"io"
)

func main() {

	url := "https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id"

	req, _ := http.NewRequest("GET", url, nil)

	req.Header.Add("xi-api-key", "xi-api-key")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```ruby
require 'uri'
require 'net/http'

url = URI("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Get.new(url)
request["xi-api-key"] = 'xi-api-key'

response = http.request(request)
puts response.read_body
```

```java
HttpResponse<String> response = Unirest.get("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id")
  .header("xi-api-key", "xi-api-key")
  .asString();
```

```php
<?php

$client = new \GuzzleHttp\Client();

$response = $client->request('GET', 'https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id', [
  'headers' => [
    'xi-api-key' => 'xi-api-key',
  ],
]);

echo $response->getBody();
```

```csharp
var client = new RestClient("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id");
var request = new RestRequest(Method.GET);
request.AddHeader("xi-api-key", "xi-api-key");
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = ["xi-api-key": "xi-api-key"]

let request = NSMutableURLRequest(url: NSURL(string: "https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "GET"
request.allHTTPHeaderFields = headers

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```
# Update knowledge base document

PATCH https://api.elevenlabs.io/v1/convai/knowledge-base/{documentation_id}
Content-Type: application/json

Update the name of a document

Reference: https://elevenlabs.io/docs/api-reference/knowledge-base/update

## OpenAPI Specification

```yaml
openapi: 3.1.1
info:
  title: Update Document
  version: endpoint_conversationalAi/knowledgeBase/documents.update
paths:
  /v1/convai/knowledge-base/{documentation_id}:
    patch:
      operationId: update
      summary: Update Document
      description: Update the name of a document
      tags:
        - - subpackage_conversationalAi
          - subpackage_conversationalAi/knowledgeBase
          - subpackage_conversationalAi/knowledgeBase/documents
      parameters:
        - name: documentation_id
          in: path
          description: >-
            The id of a document from the knowledge base. This is returned on
            document addition.
          required: true
          schema:
            type: string
        - name: xi-api-key
          in: header
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: >-
                  #/components/schemas/conversational_ai_knowledge_base_documents_update_Response_200
        '422':
          description: Validation Error
          content: {}
      requestBody:
        content:
          application/json:
            schema:
              $ref: >-
                #/components/schemas/Body_Update_document_v1_convai_knowledge_base__documentation_id__patch
components:
  schemas:
    Body_Update_document_v1_convai_knowledge_base__documentation_id__patch:
      type: object
      properties:
        name:
          type: string
      required:
        - name
    KnowledgeBaseDocumentMetadataResponseModel:
      type: object
      properties:
        created_at_unix_secs:
          type: integer
        last_updated_at_unix_secs:
          type: integer
        size_bytes:
          type: integer
      required:
        - created_at_unix_secs
        - last_updated_at_unix_secs
        - size_bytes
    DocumentUsageModeEnum:
      type: string
      enum:
        - value: prompt
        - value: auto
    ResourceAccessInfoRole:
      type: string
      enum:
        - value: admin
        - value: editor
        - value: commenter
        - value: viewer
    ResourceAccessInfo:
      type: object
      properties:
        is_creator:
          type: boolean
        creator_name:
          type: string
        creator_email:
          type: string
        role:
          $ref: '#/components/schemas/ResourceAccessInfoRole'
      required:
        - is_creator
        - creator_name
        - creator_email
        - role
    GetKnowledgeBaseURLResponseModel:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        metadata:
          $ref: '#/components/schemas/KnowledgeBaseDocumentMetadataResponseModel'
        supported_usages:
          type: array
          items:
            $ref: '#/components/schemas/DocumentUsageModeEnum'
        access_info:
          $ref: '#/components/schemas/ResourceAccessInfo'
        extracted_inner_html:
          type: string
        type:
          type: string
          enum:
            - type: stringLiteral
              value: url
        url:
          type: string
      required:
        - id
        - name
        - metadata
        - supported_usages
        - access_info
        - extracted_inner_html
        - type
        - url
    GetKnowledgeBaseFileResponseModel:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        metadata:
          $ref: '#/components/schemas/KnowledgeBaseDocumentMetadataResponseModel'
        supported_usages:
          type: array
          items:
            $ref: '#/components/schemas/DocumentUsageModeEnum'
        access_info:
          $ref: '#/components/schemas/ResourceAccessInfo'
        extracted_inner_html:
          type: string
        type:
          type: string
          enum:
            - type: stringLiteral
              value: file
      required:
        - id
        - name
        - metadata
        - supported_usages
        - access_info
        - extracted_inner_html
        - type
    GetKnowledgeBaseTextResponseModel:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        metadata:
          $ref: '#/components/schemas/KnowledgeBaseDocumentMetadataResponseModel'
        supported_usages:
          type: array
          items:
            $ref: '#/components/schemas/DocumentUsageModeEnum'
        access_info:
          $ref: '#/components/schemas/ResourceAccessInfo'
        extracted_inner_html:
          type: string
        type:
          type: string
          enum:
            - type: stringLiteral
              value: text
      required:
        - id
        - name
        - metadata
        - supported_usages
        - access_info
        - extracted_inner_html
        - type
    conversational_ai_knowledge_base_documents_update_Response_200:
      oneOf:
        - $ref: '#/components/schemas/GetKnowledgeBaseURLResponseModel'
        - $ref: '#/components/schemas/GetKnowledgeBaseFileResponseModel'
        - $ref: '#/components/schemas/GetKnowledgeBaseTextResponseModel'

```

## SDK Code Examples

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

async function main() {
    const client = new ElevenLabsClient({
        environment: "https://api.elevenlabs.io",
    });
    await client.conversationalAi.knowledgeBase.documents.update("documentation_id", {
        name: "string",
    });
}
main();

```

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(
    base_url="https://api.elevenlabs.io"
)

client.conversational_ai.knowledge_base.documents.update(
    documentation_id="documentation_id",
    name="string"
)

```

```go
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id"

	payload := strings.NewReader("{\n  \"name\": \"string\"\n}")

	req, _ := http.NewRequest("PATCH", url, payload)

	req.Header.Add("xi-api-key", "xi-api-key")
	req.Header.Add("Content-Type", "application/json")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```ruby
require 'uri'
require 'net/http'

url = URI("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Patch.new(url)
request["xi-api-key"] = 'xi-api-key'
request["Content-Type"] = 'application/json'
request.body = "{\n  \"name\": \"string\"\n}"

response = http.request(request)
puts response.read_body
```

```java
HttpResponse<String> response = Unirest.patch("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id")
  .header("xi-api-key", "xi-api-key")
  .header("Content-Type", "application/json")
  .body("{\n  \"name\": \"string\"\n}")
  .asString();
```

```php
<?php

$client = new \GuzzleHttp\Client();

$response = $client->request('PATCH', 'https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id', [
  'body' => '{
  "name": "string"
}',
  'headers' => [
    'Content-Type' => 'application/json',
    'xi-api-key' => 'xi-api-key',
  ],
]);

echo $response->getBody();
```

```csharp
var client = new RestClient("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id");
var request = new RestRequest(Method.PATCH);
request.AddHeader("xi-api-key", "xi-api-key");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"name\": \"string\"\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = [
  "xi-api-key": "xi-api-key",
  "Content-Type": "application/json"
]
let parameters = ["name": "string"] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "PATCH"
request.allHTTPHeaderFields = headers
request.httpBody = postData as Data

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```
# Create knowledge base document from URL

POST https://api.elevenlabs.io/v1/convai/knowledge-base/url
Content-Type: application/json

Create a knowledge base document generated by scraping the given webpage.

Reference: https://elevenlabs.io/docs/api-reference/knowledge-base/create-from-url

## OpenAPI Specification

```yaml
openapi: 3.1.1
info:
  title: Create Url Document
  version: endpoint_conversationalAi/knowledgeBase/documents.create_from_url
paths:
  /v1/convai/knowledge-base/url:
    post:
      operationId: create-from-url
      summary: Create Url Document
      description: >-
        Create a knowledge base document generated by scraping the given
        webpage.
      tags:
        - - subpackage_conversationalAi
          - subpackage_conversationalAi/knowledgeBase
          - subpackage_conversationalAi/knowledgeBase/documents
      parameters:
        - name: xi-api-key
          in: header
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AddKnowledgeBaseResponseModel'
        '422':
          description: Validation Error
          content: {}
      requestBody:
        content:
          application/json:
            schema:
              $ref: >-
                #/components/schemas/Body_Create_URL_document_v1_convai_knowledge_base_url_post
components:
  schemas:
    Body_Create_URL_document_v1_convai_knowledge_base_url_post:
      type: object
      properties:
        url:
          type: string
        name:
          type:
            - string
            - 'null'
      required:
        - url
    AddKnowledgeBaseResponseModel:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
      required:
        - id
        - name

```

## SDK Code Examples

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

async function main() {
    const client = new ElevenLabsClient({
        environment: "https://api.elevenlabs.io",
    });
    await client.conversationalAi.knowledgeBase.documents.createFromUrl({
        url: "string",
    });
}
main();

```

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(
    base_url="https://api.elevenlabs.io"
)

client.conversational_ai.knowledge_base.documents.create_from_url(
    url="string"
)

```

```go
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.elevenlabs.io/v1/convai/knowledge-base/url"

	payload := strings.NewReader("{\n  \"url\": \"string\"\n}")

	req, _ := http.NewRequest("POST", url, payload)

	req.Header.Add("xi-api-key", "xi-api-key")
	req.Header.Add("Content-Type", "application/json")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```ruby
require 'uri'
require 'net/http'

url = URI("https://api.elevenlabs.io/v1/convai/knowledge-base/url")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Post.new(url)
request["xi-api-key"] = 'xi-api-key'
request["Content-Type"] = 'application/json'
request.body = "{\n  \"url\": \"string\"\n}"

response = http.request(request)
puts response.read_body
```

```java
HttpResponse<String> response = Unirest.post("https://api.elevenlabs.io/v1/convai/knowledge-base/url")
  .header("xi-api-key", "xi-api-key")
  .header("Content-Type", "application/json")
  .body("{\n  \"url\": \"string\"\n}")
  .asString();
```

```php
<?php

$client = new \GuzzleHttp\Client();

$response = $client->request('POST', 'https://api.elevenlabs.io/v1/convai/knowledge-base/url', [
  'body' => '{
  "url": "string"
}',
  'headers' => [
    'Content-Type' => 'application/json',
    'xi-api-key' => 'xi-api-key',
  ],
]);

echo $response->getBody();
```

```csharp
var client = new RestClient("https://api.elevenlabs.io/v1/convai/knowledge-base/url");
var request = new RestRequest(Method.POST);
request.AddHeader("xi-api-key", "xi-api-key");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"url\": \"string\"\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = [
  "xi-api-key": "xi-api-key",
  "Content-Type": "application/json"
]
let parameters = ["url": "string"] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.elevenlabs.io/v1/convai/knowledge-base/url")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "POST"
request.allHTTPHeaderFields = headers
request.httpBody = postData as Data

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```
# Create knowledge base document from text

POST https://api.elevenlabs.io/v1/convai/knowledge-base/text
Content-Type: application/json

Create a knowledge base document containing the provided text.

Reference: https://elevenlabs.io/docs/api-reference/knowledge-base/create-from-text

## OpenAPI Specification

```yaml
openapi: 3.1.1
info:
  title: Create Text Document
  version: endpoint_conversationalAi/knowledgeBase/documents.create_from_text
paths:
  /v1/convai/knowledge-base/text:
    post:
      operationId: create-from-text
      summary: Create Text Document
      description: Create a knowledge base document containing the provided text.
      tags:
        - - subpackage_conversationalAi
          - subpackage_conversationalAi/knowledgeBase
          - subpackage_conversationalAi/knowledgeBase/documents
      parameters:
        - name: xi-api-key
          in: header
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AddKnowledgeBaseResponseModel'
        '422':
          description: Validation Error
          content: {}
      requestBody:
        content:
          application/json:
            schema:
              $ref: >-
                #/components/schemas/Body_Create_text_document_v1_convai_knowledge_base_text_post
components:
  schemas:
    Body_Create_text_document_v1_convai_knowledge_base_text_post:
      type: object
      properties:
        text:
          type: string
        name:
          type:
            - string
            - 'null'
      required:
        - text
    AddKnowledgeBaseResponseModel:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
      required:
        - id
        - name

```

## SDK Code Examples

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

async function main() {
    const client = new ElevenLabsClient({
        environment: "https://api.elevenlabs.io",
    });
    await client.conversationalAi.knowledgeBase.documents.createFromText({
        text: "string",
    });
}
main();

```

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(
    base_url="https://api.elevenlabs.io"
)

client.conversational_ai.knowledge_base.documents.create_from_text(
    text="string"
)

```

```go
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.elevenlabs.io/v1/convai/knowledge-base/text"

	payload := strings.NewReader("{\n  \"text\": \"string\"\n}")

	req, _ := http.NewRequest("POST", url, payload)

	req.Header.Add("xi-api-key", "xi-api-key")
	req.Header.Add("Content-Type", "application/json")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```ruby
require 'uri'
require 'net/http'

url = URI("https://api.elevenlabs.io/v1/convai/knowledge-base/text")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Post.new(url)
request["xi-api-key"] = 'xi-api-key'
request["Content-Type"] = 'application/json'
request.body = "{\n  \"text\": \"string\"\n}"

response = http.request(request)
puts response.read_body
```

```java
HttpResponse<String> response = Unirest.post("https://api.elevenlabs.io/v1/convai/knowledge-base/text")
  .header("xi-api-key", "xi-api-key")
  .header("Content-Type", "application/json")
  .body("{\n  \"text\": \"string\"\n}")
  .asString();
```

```php
<?php

$client = new \GuzzleHttp\Client();

$response = $client->request('POST', 'https://api.elevenlabs.io/v1/convai/knowledge-base/text', [
  'body' => '{
  "text": "string"
}',
  'headers' => [
    'Content-Type' => 'application/json',
    'xi-api-key' => 'xi-api-key',
  ],
]);

echo $response->getBody();
```

```csharp
var client = new RestClient("https://api.elevenlabs.io/v1/convai/knowledge-base/text");
var request = new RestRequest(Method.POST);
request.AddHeader("xi-api-key", "xi-api-key");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"text\": \"string\"\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = [
  "xi-api-key": "xi-api-key",
  "Content-Type": "application/json"
]
let parameters = ["text": "string"] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.elevenlabs.io/v1/convai/knowledge-base/text")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "POST"
request.allHTTPHeaderFields = headers
request.httpBody = postData as Data

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```
# Create knowledge base document from file

POST https://api.elevenlabs.io/v1/convai/knowledge-base/file
Content-Type: multipart/form-data

Create a knowledge base document generated form the uploaded file.

Reference: https://elevenlabs.io/docs/api-reference/knowledge-base/create-from-file

## OpenAPI Specification

```yaml
openapi: 3.1.1
info:
  title: Create File Document
  version: endpoint_conversationalAi/knowledgeBase/documents.create_from_file
paths:
  /v1/convai/knowledge-base/file:
    post:
      operationId: create-from-file
      summary: Create File Document
      description: Create a knowledge base document generated form the uploaded file.
      tags:
        - - subpackage_conversationalAi
          - subpackage_conversationalAi/knowledgeBase
          - subpackage_conversationalAi/knowledgeBase/documents
      parameters:
        - name: xi-api-key
          in: header
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AddKnowledgeBaseResponseModel'
        '422':
          description: Validation Error
          content: {}
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                name:
                  type:
                    - string
                    - 'null'
components:
  schemas:
    AddKnowledgeBaseResponseModel:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
      required:
        - id
        - name

```

## SDK Code Examples

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

async function main() {
    const client = new ElevenLabsClient({
        environment: "https://api.elevenlabs.io",
    });
    await client.conversationalAi.knowledgeBase.documents.createFromFile({});
}
main();

```

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(
    base_url="https://api.elevenlabs.io"
)

client.conversational_ai.knowledge_base.documents.create_from_file()

```

```go
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.elevenlabs.io/v1/convai/knowledge-base/file"

	payload := strings.NewReader("-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"file\"; filename=\"string\"\r\nContent-Type: application/octet-stream\r\n\r\n\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\n\r\n-----011000010111000001101001--\r\n")

	req, _ := http.NewRequest("POST", url, payload)

	req.Header.Add("xi-api-key", "xi-api-key")
	req.Header.Add("Content-Type", "multipart/form-data; boundary=---011000010111000001101001")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```ruby
require 'uri'
require 'net/http'

url = URI("https://api.elevenlabs.io/v1/convai/knowledge-base/file")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Post.new(url)
request["xi-api-key"] = 'xi-api-key'
request["Content-Type"] = 'multipart/form-data; boundary=---011000010111000001101001'
request.body = "-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"file\"; filename=\"string\"\r\nContent-Type: application/octet-stream\r\n\r\n\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\n\r\n-----011000010111000001101001--\r\n"

response = http.request(request)
puts response.read_body
```

```java
HttpResponse<String> response = Unirest.post("https://api.elevenlabs.io/v1/convai/knowledge-base/file")
  .header("xi-api-key", "xi-api-key")
  .header("Content-Type", "multipart/form-data; boundary=---011000010111000001101001")
  .body("-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"file\"; filename=\"string\"\r\nContent-Type: application/octet-stream\r\n\r\n\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\n\r\n-----011000010111000001101001--\r\n")
  .asString();
```

```php
<?php

$client = new \GuzzleHttp\Client();

$response = $client->request('POST', 'https://api.elevenlabs.io/v1/convai/knowledge-base/file', [
  'multipart' => [
    [
        'name' => 'file',
        'filename' => 'string',
        'contents' => null
    ]
  ]
  'headers' => [
    'xi-api-key' => 'xi-api-key',
  ],
]);

echo $response->getBody();
```

```csharp
var client = new RestClient("https://api.elevenlabs.io/v1/convai/knowledge-base/file");
var request = new RestRequest(Method.POST);
request.AddHeader("xi-api-key", "xi-api-key");
request.AddParameter("multipart/form-data; boundary=---011000010111000001101001", "-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"file\"; filename=\"string\"\r\nContent-Type: application/octet-stream\r\n\r\n\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\n\r\n-----011000010111000001101001--\r\n", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = [
  "xi-api-key": "xi-api-key",
  "Content-Type": "multipart/form-data; boundary=---011000010111000001101001"
]
let parameters = [
  [
    "name": "file",
    "fileName": "string"
  ],
  [
    "name": "name",
    "value": 
  ]
]

let boundary = "---011000010111000001101001"

var body = ""
var error: NSError? = nil
for param in parameters {
  let paramName = param["name"]!
  body += "--\(boundary)\r\n"
  body += "Content-Disposition:form-data; name=\"\(paramName)\""
  if let filename = param["fileName"] {
    let contentType = param["content-type"]!
    let fileContent = String(contentsOfFile: filename, encoding: String.Encoding.utf8)
    if (error != nil) {
      print(error as Any)
    }
    body += "; filename=\"\(filename)\"\r\n"
    body += "Content-Type: \(contentType)\r\n\r\n"
    body += fileContent
  } else if let paramValue = param["value"] {
    body += "\r\n\r\n\(paramValue)"
  }
}

let request = NSMutableURLRequest(url: NSURL(string: "https://api.elevenlabs.io/v1/convai/knowledge-base/file")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "POST"
request.allHTTPHeaderFields = headers
request.httpBody = postData as Data

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```
# Compute RAG index

POST https://api.elevenlabs.io/v1/convai/knowledge-base/{documentation_id}/rag-index
Content-Type: application/json

In case the document is not RAG indexed, it triggers rag indexing task, otherwise it just returns the current status.

Reference: https://elevenlabs.io/docs/api-reference/knowledge-base/compute-rag-index

## OpenAPI Specification

```yaml
openapi: 3.1.1
info:
  title: Compute Rag Index.
  version: endpoint_conversationalAi/knowledgeBase/document.compute_rag_index
paths:
  /v1/convai/knowledge-base/{documentation_id}/rag-index:
    post:
      operationId: compute-rag-index
      summary: Compute Rag Index.
      description: >-
        In case the document is not RAG indexed, it triggers rag indexing task,
        otherwise it just returns the current status.
      tags:
        - - subpackage_conversationalAi
          - subpackage_conversationalAi/knowledgeBase
          - subpackage_conversationalAi/knowledgeBase/document
      parameters:
        - name: documentation_id
          in: path
          description: >-
            The id of a document from the knowledge base. This is returned on
            document addition.
          required: true
          schema:
            type: string
        - name: xi-api-key
          in: header
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RAGDocumentIndexResponseModel'
        '422':
          description: Validation Error
          content: {}
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RAGIndexRequestModel'
components:
  schemas:
    EmbeddingModelEnum:
      type: string
      enum:
        - value: e5_mistral_7b_instruct
        - value: multilingual_e5_large_instruct
    RAGIndexRequestModel:
      type: object
      properties:
        model:
          $ref: '#/components/schemas/EmbeddingModelEnum'
      required:
        - model
    RAGIndexStatus:
      type: string
      enum:
        - value: created
        - value: processing
        - value: failed
        - value: succeeded
        - value: rag_limit_exceeded
        - value: document_too_small
    RAGDocumentIndexUsage:
      type: object
      properties:
        used_bytes:
          type: integer
      required:
        - used_bytes
    RAGDocumentIndexResponseModel:
      type: object
      properties:
        id:
          type: string
        model:
          $ref: '#/components/schemas/EmbeddingModelEnum'
        status:
          $ref: '#/components/schemas/RAGIndexStatus'
        progress_percentage:
          type: number
          format: double
        document_model_index_usage:
          $ref: '#/components/schemas/RAGDocumentIndexUsage'
      required:
        - id
        - model
        - status
        - progress_percentage
        - document_model_index_usage

```

## SDK Code Examples

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

async function main() {
    const client = new ElevenLabsClient({
        environment: "https://api.elevenlabs.io",
    });
    await client.conversationalAi.knowledgeBase.document.computeRagIndex("documentation_id", {
        model: "e5_mistral_7b_instruct",
    });
}
main();

```

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(
    base_url="https://api.elevenlabs.io"
)

client.conversational_ai.knowledge_base.document.compute_rag_index(
    documentation_id="documentation_id",
    model="e5_mistral_7b_instruct"
)

```

```go
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/rag-index"

	payload := strings.NewReader("{\n  \"model\": \"e5_mistral_7b_instruct\"\n}")

	req, _ := http.NewRequest("POST", url, payload)

	req.Header.Add("xi-api-key", "xi-api-key")
	req.Header.Add("Content-Type", "application/json")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```ruby
require 'uri'
require 'net/http'

url = URI("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/rag-index")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Post.new(url)
request["xi-api-key"] = 'xi-api-key'
request["Content-Type"] = 'application/json'
request.body = "{\n  \"model\": \"e5_mistral_7b_instruct\"\n}"

response = http.request(request)
puts response.read_body
```

```java
HttpResponse<String> response = Unirest.post("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/rag-index")
  .header("xi-api-key", "xi-api-key")
  .header("Content-Type", "application/json")
  .body("{\n  \"model\": \"e5_mistral_7b_instruct\"\n}")
  .asString();
```

```php
<?php

$client = new \GuzzleHttp\Client();

$response = $client->request('POST', 'https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/rag-index', [
  'body' => '{
  "model": "e5_mistral_7b_instruct"
}',
  'headers' => [
    'Content-Type' => 'application/json',
    'xi-api-key' => 'xi-api-key',
  ],
]);

echo $response->getBody();
```

```csharp
var client = new RestClient("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/rag-index");
var request = new RestRequest(Method.POST);
request.AddHeader("xi-api-key", "xi-api-key");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"model\": \"e5_mistral_7b_instruct\"\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = [
  "xi-api-key": "xi-api-key",
  "Content-Type": "application/json"
]
let parameters = ["model": "e5_mistral_7b_instruct"] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/rag-index")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "POST"
request.allHTTPHeaderFields = headers
request.httpBody = postData as Data

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```
# Get RAG index

GET https://api.elevenlabs.io/v1/convai/knowledge-base/{documentation_id}/rag-index

Provides information about all RAG indexes of the specified knowledgebase document.

Reference: https://elevenlabs.io/docs/api-reference/knowledge-base/get-document-rag-indexes

## OpenAPI Specification

```yaml
openapi: 3.1.1
info:
  title: Get Rag Indexes Of The Specified Knowledgebase Document.
  version: endpoint_conversationalAi.get_document_rag_indexes
paths:
  /v1/convai/knowledge-base/{documentation_id}/rag-index:
    get:
      operationId: get-document-rag-indexes
      summary: Get Rag Indexes Of The Specified Knowledgebase Document.
      description: >-
        Provides information about all RAG indexes of the specified
        knowledgebase document.
      tags:
        - - subpackage_conversationalAi
      parameters:
        - name: documentation_id
          in: path
          description: >-
            The id of a document from the knowledge base. This is returned on
            document addition.
          required: true
          schema:
            type: string
        - name: xi-api-key
          in: header
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RAGDocumentIndexesResponseModel'
        '422':
          description: Validation Error
          content: {}
components:
  schemas:
    EmbeddingModelEnum:
      type: string
      enum:
        - value: e5_mistral_7b_instruct
        - value: multilingual_e5_large_instruct
    RAGIndexStatus:
      type: string
      enum:
        - value: created
        - value: processing
        - value: failed
        - value: succeeded
        - value: rag_limit_exceeded
        - value: document_too_small
    RAGDocumentIndexUsage:
      type: object
      properties:
        used_bytes:
          type: integer
      required:
        - used_bytes
    RAGDocumentIndexResponseModel:
      type: object
      properties:
        id:
          type: string
        model:
          $ref: '#/components/schemas/EmbeddingModelEnum'
        status:
          $ref: '#/components/schemas/RAGIndexStatus'
        progress_percentage:
          type: number
          format: double
        document_model_index_usage:
          $ref: '#/components/schemas/RAGDocumentIndexUsage'
      required:
        - id
        - model
        - status
        - progress_percentage
        - document_model_index_usage
    RAGDocumentIndexesResponseModel:
      type: object
      properties:
        indexes:
          type: array
          items:
            $ref: '#/components/schemas/RAGDocumentIndexResponseModel'
      required:
        - indexes

```

## SDK Code Examples

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

async function main() {
    const client = new ElevenLabsClient({
        environment: "https://api.elevenlabs.io",
    });
    await client.conversationalAi.getDocumentRagIndexes("documentation_id");
}
main();

```

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(
    base_url="https://api.elevenlabs.io"
)

client.conversational_ai.get_document_rag_indexes(
    documentation_id="documentation_id"
)

```

```go
package main

import (
	"fmt"
	"net/http"
	"io"
)

func main() {

	url := "https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/rag-index"

	req, _ := http.NewRequest("GET", url, nil)

	req.Header.Add("xi-api-key", "xi-api-key")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```ruby
require 'uri'
require 'net/http'

url = URI("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/rag-index")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Get.new(url)
request["xi-api-key"] = 'xi-api-key'

response = http.request(request)
puts response.read_body
```

```java
HttpResponse<String> response = Unirest.get("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/rag-index")
  .header("xi-api-key", "xi-api-key")
  .asString();
```

```php
<?php

$client = new \GuzzleHttp\Client();

$response = $client->request('GET', 'https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/rag-index', [
  'headers' => [
    'xi-api-key' => 'xi-api-key',
  ],
]);

echo $response->getBody();
```

```csharp
var client = new RestClient("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/rag-index");
var request = new RestRequest(Method.GET);
request.AddHeader("xi-api-key", "xi-api-key");
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = ["xi-api-key": "xi-api-key"]

let request = NSMutableURLRequest(url: NSURL(string: "https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/rag-index")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "GET"
request.allHTTPHeaderFields = headers

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```
# Get RAG index overview

GET https://api.elevenlabs.io/v1/convai/knowledge-base/rag-index

Provides total size and other information of RAG indexes used by knowledgebase documents

Reference: https://elevenlabs.io/docs/api-reference/knowledge-base/rag-index-overview

## OpenAPI Specification

```yaml
openapi: 3.1.1
info:
  title: Get Rag Index Overview.
  version: endpoint_conversationalAi.rag_index_overview
paths:
  /v1/convai/knowledge-base/rag-index:
    get:
      operationId: rag-index-overview
      summary: Get Rag Index Overview.
      description: >-
        Provides total size and other information of RAG indexes used by
        knowledgebase documents
      tags:
        - - subpackage_conversationalAi
      parameters:
        - name: xi-api-key
          in: header
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RAGIndexOverviewResponseModel'
        '422':
          description: Validation Error
          content: {}
components:
  schemas:
    EmbeddingModelEnum:
      type: string
      enum:
        - value: e5_mistral_7b_instruct
        - value: multilingual_e5_large_instruct
    RAGIndexOverviewEmbeddingModelResponseModel:
      type: object
      properties:
        model:
          $ref: '#/components/schemas/EmbeddingModelEnum'
        used_bytes:
          type: integer
      required:
        - model
        - used_bytes
    RAGIndexOverviewResponseModel:
      type: object
      properties:
        total_used_bytes:
          type: integer
        total_max_bytes:
          type: integer
        models:
          type: array
          items:
            $ref: '#/components/schemas/RAGIndexOverviewEmbeddingModelResponseModel'
      required:
        - total_used_bytes
        - total_max_bytes
        - models

```

## SDK Code Examples

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

async function main() {
    const client = new ElevenLabsClient({
        environment: "https://api.elevenlabs.io",
    });
    await client.conversationalAi.ragIndexOverview();
}
main();

```

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(
    base_url="https://api.elevenlabs.io"
)

client.conversational_ai.rag_index_overview()

```

```go
package main

import (
	"fmt"
	"net/http"
	"io"
)

func main() {

	url := "https://api.elevenlabs.io/v1/convai/knowledge-base/rag-index"

	req, _ := http.NewRequest("GET", url, nil)

	req.Header.Add("xi-api-key", "xi-api-key")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```ruby
require 'uri'
require 'net/http'

url = URI("https://api.elevenlabs.io/v1/convai/knowledge-base/rag-index")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Get.new(url)
request["xi-api-key"] = 'xi-api-key'

response = http.request(request)
puts response.read_body
```

```java
HttpResponse<String> response = Unirest.get("https://api.elevenlabs.io/v1/convai/knowledge-base/rag-index")
  .header("xi-api-key", "xi-api-key")
  .asString();
```

```php
<?php

$client = new \GuzzleHttp\Client();

$response = $client->request('GET', 'https://api.elevenlabs.io/v1/convai/knowledge-base/rag-index', [
  'headers' => [
    'xi-api-key' => 'xi-api-key',
  ],
]);

echo $response->getBody();
```

```csharp
var client = new RestClient("https://api.elevenlabs.io/v1/convai/knowledge-base/rag-index");
var request = new RestRequest(Method.GET);
request.AddHeader("xi-api-key", "xi-api-key");
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = ["xi-api-key": "xi-api-key"]

let request = NSMutableURLRequest(url: NSURL(string: "https://api.elevenlabs.io/v1/convai/knowledge-base/rag-index")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "GET"
request.allHTTPHeaderFields = headers

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```
# Delete RAG index

DELETE https://api.elevenlabs.io/v1/convai/knowledge-base/{documentation_id}/rag-index/{rag_index_id}

Delete RAG index for the knowledgebase document.

Reference: https://elevenlabs.io/docs/api-reference/knowledge-base/delete-document-rag-index

## OpenAPI Specification

```yaml
openapi: 3.1.1
info:
  title: Delete Rag Index.
  version: endpoint_conversationalAi.delete_document_rag_index
paths:
  /v1/convai/knowledge-base/{documentation_id}/rag-index/{rag_index_id}:
    delete:
      operationId: delete-document-rag-index
      summary: Delete Rag Index.
      description: Delete RAG index for the knowledgebase document.
      tags:
        - - subpackage_conversationalAi
      parameters:
        - name: documentation_id
          in: path
          description: >-
            The id of a document from the knowledge base. This is returned on
            document addition.
          required: true
          schema:
            type: string
        - name: rag_index_id
          in: path
          description: The id of RAG index of document from the knowledge base.
          required: true
          schema:
            type: string
        - name: xi-api-key
          in: header
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RAGDocumentIndexResponseModel'
        '422':
          description: Validation Error
          content: {}
components:
  schemas:
    EmbeddingModelEnum:
      type: string
      enum:
        - value: e5_mistral_7b_instruct
        - value: multilingual_e5_large_instruct
    RAGIndexStatus:
      type: string
      enum:
        - value: created
        - value: processing
        - value: failed
        - value: succeeded
        - value: rag_limit_exceeded
        - value: document_too_small
    RAGDocumentIndexUsage:
      type: object
      properties:
        used_bytes:
          type: integer
      required:
        - used_bytes
    RAGDocumentIndexResponseModel:
      type: object
      properties:
        id:
          type: string
        model:
          $ref: '#/components/schemas/EmbeddingModelEnum'
        status:
          $ref: '#/components/schemas/RAGIndexStatus'
        progress_percentage:
          type: number
          format: double
        document_model_index_usage:
          $ref: '#/components/schemas/RAGDocumentIndexUsage'
      required:
        - id
        - model
        - status
        - progress_percentage
        - document_model_index_usage

```

## SDK Code Examples

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

async function main() {
    const client = new ElevenLabsClient({
        environment: "https://api.elevenlabs.io",
    });
    await client.conversationalAi.deleteDocumentRagIndex("documentation_id", "rag_index_id");
}
main();

```

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(
    base_url="https://api.elevenlabs.io"
)

client.conversational_ai.delete_document_rag_index(
    documentation_id="documentation_id",
    rag_index_id="rag_index_id"
)

```

```go
package main

import (
	"fmt"
	"net/http"
	"io"
)

func main() {

	url := "https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/rag-index/rag_index_id"

	req, _ := http.NewRequest("DELETE", url, nil)

	req.Header.Add("xi-api-key", "xi-api-key")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```ruby
require 'uri'
require 'net/http'

url = URI("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/rag-index/rag_index_id")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Delete.new(url)
request["xi-api-key"] = 'xi-api-key'

response = http.request(request)
puts response.read_body
```

```java
HttpResponse<String> response = Unirest.delete("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/rag-index/rag_index_id")
  .header("xi-api-key", "xi-api-key")
  .asString();
```

```php
<?php

$client = new \GuzzleHttp\Client();

$response = $client->request('DELETE', 'https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/rag-index/rag_index_id', [
  'headers' => [
    'xi-api-key' => 'xi-api-key',
  ],
]);

echo $response->getBody();
```

```csharp
var client = new RestClient("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/rag-index/rag_index_id");
var request = new RestRequest(Method.DELETE);
request.AddHeader("xi-api-key", "xi-api-key");
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = ["xi-api-key": "xi-api-key"]

let request = NSMutableURLRequest(url: NSURL(string: "https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/rag-index/rag_index_id")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "DELETE"
request.allHTTPHeaderFields = headers

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```
# Get dependent agents

GET https://api.elevenlabs.io/v1/convai/knowledge-base/{documentation_id}/dependent-agents

Get a list of agents depending on this knowledge base document

Reference: https://elevenlabs.io/docs/api-reference/knowledge-base/get-agents

## OpenAPI Specification

```yaml
openapi: 3.1.1
info:
  title: Get Dependent Agents List
  version: endpoint_conversationalAi/knowledgeBase/documents.get_agents
paths:
  /v1/convai/knowledge-base/{documentation_id}/dependent-agents:
    get:
      operationId: get-agents
      summary: Get Dependent Agents List
      description: Get a list of agents depending on this knowledge base document
      tags:
        - - subpackage_conversationalAi
          - subpackage_conversationalAi/knowledgeBase
          - subpackage_conversationalAi/knowledgeBase/documents
      parameters:
        - name: documentation_id
          in: path
          description: >-
            The id of a document from the knowledge base. This is returned on
            document addition.
          required: true
          schema:
            type: string
        - name: cursor
          in: query
          description: Used for fetching next page. Cursor is returned in the response.
          required: false
          schema:
            type:
              - string
              - 'null'
        - name: page_size
          in: query
          description: >-
            How many documents to return at maximum. Can not exceed 100,
            defaults to 30.
          required: false
          schema:
            type: integer
        - name: xi-api-key
          in: header
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: >-
                  #/components/schemas/GetKnowledgeBaseDependentAgentsResponseModel
        '422':
          description: Validation Error
          content: {}
components:
  schemas:
    DependentAvailableAgentIdentifierAccessLevel:
      type: string
      enum:
        - value: admin
        - value: editor
        - value: commenter
        - value: viewer
    DependentAvailableAgentIdentifier:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        type:
          type: string
          enum:
            - type: stringLiteral
              value: available
        created_at_unix_secs:
          type: integer
        access_level:
          $ref: '#/components/schemas/DependentAvailableAgentIdentifierAccessLevel'
      required:
        - id
        - name
        - created_at_unix_secs
        - access_level
    DependentUnknownAgentIdentifier:
      type: object
      properties:
        type:
          type: string
          enum:
            - type: stringLiteral
              value: unknown
    GetKnowledgeBaseDependentAgentsResponseModelAgentsItems:
      oneOf:
        - $ref: '#/components/schemas/DependentAvailableAgentIdentifier'
        - $ref: '#/components/schemas/DependentUnknownAgentIdentifier'
    GetKnowledgeBaseDependentAgentsResponseModel:
      type: object
      properties:
        agents:
          type: array
          items:
            $ref: >-
              #/components/schemas/GetKnowledgeBaseDependentAgentsResponseModelAgentsItems
        next_cursor:
          type:
            - string
            - 'null'
        has_more:
          type: boolean
      required:
        - agents
        - has_more

```

## SDK Code Examples

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

async function main() {
    const client = new ElevenLabsClient({
        environment: "https://api.elevenlabs.io",
    });
    await client.conversationalAi.knowledgeBase.documents.getAgents("documentation_id", {});
}
main();

```

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(
    base_url="https://api.elevenlabs.io"
)

client.conversational_ai.knowledge_base.documents.get_agents(
    documentation_id="documentation_id"
)

```

```go
package main

import (
	"fmt"
	"net/http"
	"io"
)

func main() {

	url := "https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/dependent-agents"

	req, _ := http.NewRequest("GET", url, nil)

	req.Header.Add("xi-api-key", "xi-api-key")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```ruby
require 'uri'
require 'net/http'

url = URI("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/dependent-agents")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Get.new(url)
request["xi-api-key"] = 'xi-api-key'

response = http.request(request)
puts response.read_body
```

```java
HttpResponse<String> response = Unirest.get("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/dependent-agents")
  .header("xi-api-key", "xi-api-key")
  .asString();
```

```php
<?php

$client = new \GuzzleHttp\Client();

$response = $client->request('GET', 'https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/dependent-agents', [
  'headers' => [
    'xi-api-key' => 'xi-api-key',
  ],
]);

echo $response->getBody();
```

```csharp
var client = new RestClient("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/dependent-agents");
var request = new RestRequest(Method.GET);
request.AddHeader("xi-api-key", "xi-api-key");
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = ["xi-api-key": "xi-api-key"]

let request = NSMutableURLRequest(url: NSURL(string: "https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/dependent-agents")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "GET"
request.allHTTPHeaderFields = headers

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```
# Get document content

GET https://api.elevenlabs.io/v1/convai/knowledge-base/{documentation_id}/content

Get the entire content of a document from the knowledge base

Reference: https://elevenlabs.io/docs/api-reference/knowledge-base/get-content

## OpenAPI Specification

```yaml
openapi: 3.1.1
info:
  title: Get Document Content
  version: endpoint_conversationalAi/knowledgeBase/documents.get_content
paths:
  /v1/convai/knowledge-base/{documentation_id}/content:
    get:
      operationId: get-content
      summary: Get Document Content
      description: Get the entire content of a document from the knowledge base
      tags:
        - - subpackage_conversationalAi
          - subpackage_conversationalAi/knowledgeBase
          - subpackage_conversationalAi/knowledgeBase/documents
      parameters:
        - name: documentation_id
          in: path
          description: >-
            The id of a document from the knowledge base. This is returned on
            document addition.
          required: true
          schema:
            type: string
        - name: xi-api-key
          in: header
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Streaming document content
          content:
            application/json:
              schema:
                $ref: >-
                  #/components/schemas/conversational_ai_knowledge_base_documents_get_content_Response_200
        '422':
          description: Validation Error
          content: {}
components:
  schemas:
    conversational_ai_knowledge_base_documents_get_content_Response_200:
      type: object
      properties: {}

```

## SDK Code Examples

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

async function main() {
    const client = new ElevenLabsClient({
        environment: "https://api.elevenlabs.io",
    });
    await client.conversationalAi.knowledgeBase.documents.getContent("documentation_id");
}
main();

```

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(
    base_url="https://api.elevenlabs.io"
)

client.conversational_ai.knowledge_base.documents.get_content(
    documentation_id="documentation_id"
)

```

```go
package main

import (
	"fmt"
	"net/http"
	"io"
)

func main() {

	url := "https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/content"

	req, _ := http.NewRequest("GET", url, nil)

	req.Header.Add("xi-api-key", "xi-api-key")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```ruby
require 'uri'
require 'net/http'

url = URI("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/content")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Get.new(url)
request["xi-api-key"] = 'xi-api-key'

response = http.request(request)
puts response.read_body
```

```java
HttpResponse<String> response = Unirest.get("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/content")
  .header("xi-api-key", "xi-api-key")
  .asString();
```

```php
<?php

$client = new \GuzzleHttp\Client();

$response = $client->request('GET', 'https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/content', [
  'headers' => [
    'xi-api-key' => 'xi-api-key',
  ],
]);

echo $response->getBody();
```

```csharp
var client = new RestClient("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/content");
var request = new RestRequest(Method.GET);
request.AddHeader("xi-api-key", "xi-api-key");
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = ["xi-api-key": "xi-api-key"]

let request = NSMutableURLRequest(url: NSURL(string: "https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/content")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "GET"
request.allHTTPHeaderFields = headers

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```
# Get document chunk

GET https://api.elevenlabs.io/v1/convai/knowledge-base/{documentation_id}/chunk/{chunk_id}

Get details about a specific documentation part used by RAG.

Reference: https://elevenlabs.io/docs/api-reference/knowledge-base/get-chunk

## OpenAPI Specification

```yaml
openapi: 3.1.1
info:
  title: Get Documentation Chunk From Knowledge Base
  version: endpoint_conversationalAi/knowledgeBase/documents/chunk.get
paths:
  /v1/convai/knowledge-base/{documentation_id}/chunk/{chunk_id}:
    get:
      operationId: get
      summary: Get Documentation Chunk From Knowledge Base
      description: Get details about a specific documentation part used by RAG.
      tags:
        - - subpackage_conversationalAi
          - subpackage_conversationalAi/knowledgeBase
          - subpackage_conversationalAi/knowledgeBase/documents
          - subpackage_conversationalAi/knowledgeBase/documents/chunk
      parameters:
        - name: documentation_id
          in: path
          description: >-
            The id of a document from the knowledge base. This is returned on
            document addition.
          required: true
          schema:
            type: string
        - name: chunk_id
          in: path
          description: The id of a document RAG chunk from the knowledge base.
          required: true
          schema:
            type: string
        - name: xi-api-key
          in: header
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/KnowledgeBaseDocumentChunkResponseModel'
        '422':
          description: Validation Error
          content: {}
components:
  schemas:
    KnowledgeBaseDocumentChunkResponseModel:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        content:
          type: string
      required:
        - id
        - name
        - content

```

## SDK Code Examples

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

async function main() {
    const client = new ElevenLabsClient({
        environment: "https://api.elevenlabs.io",
    });
    await client.conversationalAi.knowledgeBase.documents.chunk.get("documentation_id", "chunk_id");
}
main();

```

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(
    base_url="https://api.elevenlabs.io"
)

client.conversational_ai.knowledge_base.documents.chunk.get(
    documentation_id="documentation_id",
    chunk_id="chunk_id"
)

```

```go
package main

import (
	"fmt"
	"net/http"
	"io"
)

func main() {

	url := "https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/chunk/chunk_id"

	req, _ := http.NewRequest("GET", url, nil)

	req.Header.Add("xi-api-key", "xi-api-key")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```ruby
require 'uri'
require 'net/http'

url = URI("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/chunk/chunk_id")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Get.new(url)
request["xi-api-key"] = 'xi-api-key'

response = http.request(request)
puts response.read_body
```

```java
HttpResponse<String> response = Unirest.get("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/chunk/chunk_id")
  .header("xi-api-key", "xi-api-key")
  .asString();
```

```php
<?php

$client = new \GuzzleHttp\Client();

$response = $client->request('GET', 'https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/chunk/chunk_id', [
  'headers' => [
    'xi-api-key' => 'xi-api-key',
  ],
]);

echo $response->getBody();
```

```csharp
var client = new RestClient("https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/chunk/chunk_id");
var request = new RestRequest(Method.GET);
request.AddHeader("xi-api-key", "xi-api-key");
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = ["xi-api-key": "xi-api-key"]

let request = NSMutableURLRequest(url: NSURL(string: "https://api.elevenlabs.io/v1/convai/knowledge-base/documentation_id/chunk/chunk_id")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "GET"
request.allHTTPHeaderFields = headers

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```
# Get knowledge base size

GET https://api.elevenlabs.io/v1/convai/agent/{agent_id}/knowledge-base/size

Returns the number of pages in the agent's knowledge base.

Reference: https://elevenlabs.io/docs/api-reference/knowledge-base/size

## OpenAPI Specification

```yaml
openapi: 3.1.1
info:
  title: Returns The Size Of The Agent'S Knowledge Base
  version: endpoint_conversationalAi/agents/knowledgeBase.size
paths:
  /v1/convai/agent/{agent_id}/knowledge-base/size:
    get:
      operationId: size
      summary: Returns The Size Of The Agent'S Knowledge Base
      description: Returns the number of pages in the agent's knowledge base.
      tags:
        - - subpackage_conversationalAi
          - subpackage_conversationalAi/agents
          - subpackage_conversationalAi/agents/knowledgeBase
      parameters:
        - name: agent_id
          in: path
          required: true
          schema:
            type: string
        - name: xi-api-key
          in: header
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GetAgentKnowledgebaseSizeResponseModel'
        '422':
          description: Validation Error
          content: {}
components:
  schemas:
    GetAgentKnowledgebaseSizeResponseModel:
      type: object
      properties:
        number_of_pages:
          type: number
          format: double
      required:
        - number_of_pages

```

## SDK Code Examples

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

async function main() {
    const client = new ElevenLabsClient({
        environment: "https://api.elevenlabs.io",
    });
    await client.conversationalAi.agents.knowledgeBase.size("agent_id");
}
main();

```

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(
    base_url="https://api.elevenlabs.io"
)

client.conversational_ai.agents.knowledge_base.size(
    agent_id="agent_id"
)

```

```go
package main

import (
	"fmt"
	"net/http"
	"io"
)

func main() {

	url := "https://api.elevenlabs.io/v1/convai/agent/agent_id/knowledge-base/size"

	req, _ := http.NewRequest("GET", url, nil)

	req.Header.Add("xi-api-key", "xi-api-key")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```ruby
require 'uri'
require 'net/http'

url = URI("https://api.elevenlabs.io/v1/convai/agent/agent_id/knowledge-base/size")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Get.new(url)
request["xi-api-key"] = 'xi-api-key'

response = http.request(request)
puts response.read_body
```

```java
HttpResponse<String> response = Unirest.get("https://api.elevenlabs.io/v1/convai/agent/agent_id/knowledge-base/size")
  .header("xi-api-key", "xi-api-key")
  .asString();
```

```php
<?php

$client = new \GuzzleHttp\Client();

$response = $client->request('GET', 'https://api.elevenlabs.io/v1/convai/agent/agent_id/knowledge-base/size', [
  'headers' => [
    'xi-api-key' => 'xi-api-key',
  ],
]);

echo $response->getBody();
```

```csharp
var client = new RestClient("https://api.elevenlabs.io/v1/convai/agent/agent_id/knowledge-base/size");
var request = new RestRequest(Method.GET);
request.AddHeader("xi-api-key", "xi-api-key");
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = ["xi-api-key": "xi-api-key"]

let request = NSMutableURLRequest(url: NSURL(string: "https://api.elevenlabs.io/v1/convai/agent/agent_id/knowledge-base/size")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "GET"
request.allHTTPHeaderFields = headers

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```

