#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Copyright 2024, by the California Institute of Technology. ALL RIGHTS RESERVED.
#  United States Government Sponsorship acknowledged. Any commercial use must be
#  negotiated with the Office of Technology Transfer at the California Institute of
#  Technology.  This software is subject to U.S. export control laws and regulations
#  and has been classified as EAR99.  By accepting this software, the user agrees to
#  comply with all applicable U.S. export laws and regulations.  User has the
#  responsibility to obtain export licenses, or other export authority as may be
#  required before exporting such information to foreign countries or providing
#  access to foreign persons.
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

process_schema = {
        "$schema": "http://json-schema.org/draft-04/schema",
        "allOf": [
            {
                "allOf": [
                    {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string"
                            },
                            "description": {
                                "type": "string"
                            },
                            "keywords": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "metadata": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {
                                            "type": "string"
                                        },
                                        "role": {
                                            "type": "string"
                                        },
                                        "href": {
                                            "type": "string"
                                        }
                                    }
                                }
                            },
                            "additionalParameters": {
                                "allOf": [
                                    {
                                        "type": "object",
                                        "properties": {
                                            "title": {
                                                "type": "string"
                                            },
                                            "role": {
                                                "type": "string"
                                            },
                                            "href": {
                                                "type": "string"
                                            }
                                        }
                                    },
                                    {
                                        "type": "object",
                                        "properties": {
                                            "parameters": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "required": [
                                                        "name",
                                                        "value"
                                                    ],
                                                    "properties": {
                                                        "name": {
                                                            "type": "string"
                                                        },
                                                        "value": {
                                                            "type": "array",
                                                            "items": {
                                                                "anyOf": [
                                                                    {
                                                                        "type": "string"
                                                                    },
                                                                    {
                                                                        "type": "number"
                                                                    },
                                                                    {
                                                                        "type": "integer"
                                                                    },
                                                                    {
                                                                        "type": "array",
                                                                        "items": {}
                                                                    },
                                                                    {
                                                                        "type": "object"
                                                                    }
                                                                ]
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    {
                        "type": "object",
                        "required": [
                            "id",
                            "version"
                        ],
                        "properties": {
                            "id": {
                                "type": "string"
                            },
                            "version": {
                                "type": "string"
                            },
                            "jobControlOptions": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": [
                                        "sync-execute",
                                        "async-execute",
                                        "dismiss"
                                    ]
                                }
                            },
                            "outputTransmission": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": [
                                        "value",
                                        "reference"
                                    ],
                                    "default": "value"
                                }
                            },
                            "links": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": [
                                        "href"
                                    ],
                                    "properties": {
                                        "href": {
                                            "type": "string"
                                        },
                                        "rel": {
                                            "type": "string",
                                            "example": "service"
                                        },
                                        "type": {
                                            "type": "string",
                                            "example": "application/json"
                                        },
                                        "hreflang": {
                                            "type": "string",
                                            "example": "en"
                                        },
                                        "title": {
                                            "type": "string"
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]
            },
            {
                "type": "object",
                "properties": {
                    "inputs": {
                        "additionalProperties": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "properties": {
                                        "title": {
                                            "type": "string"
                                        },
                                        "description": {
                                            "type": "string"
                                        },
                                        "keywords": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "metadata": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "title": {
                                                        "type": "string"
                                                    },
                                                    "role": {
                                                        "type": "string"
                                                    },
                                                    "href": {
                                                        "type": "string"
                                                    }
                                                }
                                            }
                                        },
                                        "additionalParameters": {
                                            "allOf": [
                                                {
                                                    "type": "object",
                                                    "properties": {
                                                        "title": {
                                                            "type": "string"
                                                        },
                                                        "role": {
                                                            "type": "string"
                                                        },
                                                        "href": {
                                                            "type": "string"
                                                        }
                                                    }
                                                },
                                                {
                                                    "type": "object",
                                                    "properties": {
                                                        "parameters": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "object",
                                                                "required": [
                                                                    "name",
                                                                    "value"
                                                                ],
                                                                "properties": {
                                                                    "name": {
                                                                        "type": "string"
                                                                    },
                                                                    "value": {
                                                                        "type": "array",
                                                                        "items": {
                                                                            "anyOf": [
                                                                                {
                                                                                    "type": "string"
                                                                                },
                                                                                {
                                                                                    "type": "number"
                                                                                },
                                                                                {
                                                                                    "type": "integer"
                                                                                },
                                                                                {
                                                                                    "type": "array",
                                                                                    "items": {}
                                                                                },
                                                                                {
                                                                                    "type": "object"
                                                                                }
                                                                            ]
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                },
                                {
                                    "type": "object",
                                    "required": [
                                        "schema"
                                    ],
                                    "properties": {
                                        "minOccurs": {
                                            "type": "integer",
                                            "default": 1
                                        },
                                        "maxOccurs": {
                                            "anyOf": [
                                                {
                                                    "type": "integer",
                                                    "default": 1
                                                },
                                                {
                                                    "type": "string",
                                                    "enum": [
                                                        "unbounded"
                                                    ]
                                                }
                                            ]
                                        },
                                        "schema": {
                                            "anyOf": [
                                                {
                                                    "type": "object",
                                                    "required": [
                                                        "$ref"
                                                    ],
                                                    "properties": {
                                                        "$ref": {
                                                            "type": "string",
                                                            "format": "uri-reference"
                                                        }
                                                    }
                                                },
                                                {
                                                    "type": "object",
                                                    "properties": {
                                                        "title": {
                                                            "type": "string"
                                                        },
                                                        "multipleOf": {
                                                            "type": "number",
                                                            "minimum": 0,
                                                            "exclusiveMinimum": True
                                                        },
                                                        "maximum": {
                                                            "type": "number"
                                                        },
                                                        "exclusiveMaximum": {
                                                            "type": "boolean",
                                                            "default": False
                                                        },
                                                        "minimum": {
                                                            "type": "number"
                                                        },
                                                        "exclusiveMinimum": {
                                                            "type": "boolean",
                                                            "default": False
                                                        },
                                                        "maxLength": {
                                                            "type": "integer",
                                                            "minimum": 0
                                                        },
                                                        "minLength": {
                                                            "type": "integer",
                                                            "minimum": 0,
                                                            "default": 0
                                                        },
                                                        "pattern": {
                                                            "type": "string",
                                                            "format": "regex"
                                                        },
                                                        "maxItems": {
                                                            "type": "integer",
                                                            "minimum": 0
                                                        },
                                                        "minItems": {
                                                            "type": "integer",
                                                            "minimum": 0,
                                                            "default": 0
                                                        },
                                                        "uniqueItems": {
                                                            "type": "boolean",
                                                            "default": False
                                                        },
                                                        "maxProperties": {
                                                            "type": "integer",
                                                            "minimum": 0
                                                        },
                                                        "minProperties": {
                                                            "type": "integer",
                                                            "minimum": 0,
                                                            "default": 0
                                                        },
                                                        "required": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "string"
                                                            },
                                                            "minItems": 1,
                                                            "uniqueItems": True
                                                        },
                                                        "enum": {
                                                            "type": "array",
                                                            "items": {},
                                                            "minItems": 1,
                                                            "uniqueItems": False
                                                        },
                                                        "type": {
                                                            "type": "string",
                                                            "enum": [
                                                                "array",
                                                                "boolean",
                                                                "integer",
                                                                "number",
                                                                "object",
                                                                "string"
                                                            ]
                                                        },
                                                        "not": {
                                                            "anyOf": [
                                                                {
                                                                    "type": "object",
                                                                    "required": [
                                                                        "$ref"
                                                                    ],
                                                                    "properties": {
                                                                        "$ref": {
                                                                            "type": "string",
                                                                            "format": "uri-reference"
                                                                        }
                                                                    }
                                                                }
                                                            ]
                                                        },
                                                        "allOf": {
                                                            "type": "array",
                                                            "items": {
                                                                "anyOf": [
                                                                    {
                                                                        "type": "object",
                                                                        "required": [
                                                                            "$ref"
                                                                        ],
                                                                        "properties": {
                                                                            "$ref": {
                                                                                "type": "string",
                                                                                "format": "uri-reference"
                                                                            }
                                                                        }
                                                                    }
                                                                ]
                                                            }
                                                        },
                                                        "anyOf": {
                                                            "type": "array",
                                                            "items": {
                                                                "anyOf": [
                                                                    {
                                                                        "type": "object",
                                                                        "required": [
                                                                            "$ref"
                                                                        ],
                                                                        "properties": {
                                                                            "$ref": {
                                                                                "type": "string",
                                                                                "format": "uri-reference"
                                                                            }
                                                                        }
                                                                    }
                                                                ]
                                                            }
                                                        },
                                                        "items": {
                                                            "anyOf": [
                                                                {
                                                                    "type": "object",
                                                                    "required": [
                                                                        "$ref"
                                                                    ],
                                                                    "properties": {
                                                                        "$ref": {
                                                                            "type": "string",
                                                                            "format": "uri-reference"
                                                                        }
                                                                    }
                                                                }
                                                            ]
                                                        },
                                                        "properties": {
                                                            "type": "object",
                                                            "additionalProperties": {
                                                                "anyOf": [
                                                                    {
                                                                        "type": "object",
                                                                        "required": [
                                                                            "$ref"
                                                                        ],
                                                                        "properties": {
                                                                            "$ref": {
                                                                                "type": "string",
                                                                                "format": "uri-reference"
                                                                            }
                                                                        }
                                                                    }
                                                                ]
                                                            }
                                                        },
                                                        "additionalProperties": {
                                                            "anyOf": [
                                                                {
                                                                    "type": "object",
                                                                    "required": [
                                                                        "$ref"
                                                                    ],
                                                                    "properties": {
                                                                        "$ref": {
                                                                            "type": "string",
                                                                            "format": "uri-reference"
                                                                        }
                                                                    }
                                                                },
                                                                {
                                                                    "type": "boolean"
                                                                }
                                                            ],
                                                            "default": True
                                                        },
                                                        "description": {
                                                            "type": "string"
                                                        },
                                                        "format": {
                                                            "type": "string"
                                                        },
                                                        "default": {},
                                                        "nullable": {
                                                            "type": "boolean",
                                                            "default": False
                                                        },
                                                        "readOnly": {
                                                            "type": "boolean",
                                                            "default": False
                                                        },
                                                        "writeOnly": {
                                                            "type": "boolean",
                                                            "default": False
                                                        },
                                                        "example": {},
                                                        "deprecated": {
                                                            "type": "boolean",
                                                            "default": False
                                                        },
                                                        "contentMediaType": {
                                                            "type": "string"
                                                        },
                                                        "contentEncoding": {
                                                            "type": "string"
                                                        },
                                                        "contentSchema": {
                                                            "type": "string"
                                                        }
                                                    },
                                                    "additionalProperties": False
                                                }
                                            ]
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "outputs": {
                        "additionalProperties": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "properties": {
                                        "title": {
                                            "type": "string"
                                        },
                                        "description": {
                                            "type": "string"
                                        },
                                        "keywords": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "metadata": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "title": {
                                                        "type": "string"
                                                    },
                                                    "role": {
                                                        "type": "string"
                                                    },
                                                    "href": {
                                                        "type": "string"
                                                    }
                                                }
                                            }
                                        },
                                        "additionalParameters": {
                                            "allOf": [
                                                {
                                                    "type": "object",
                                                    "properties": {
                                                        "title": {
                                                            "type": "string"
                                                        },
                                                        "role": {
                                                            "type": "string"
                                                        },
                                                        "href": {
                                                            "type": "string"
                                                        }
                                                    }
                                                },
                                                {
                                                    "type": "object",
                                                    "properties": {
                                                        "parameters": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "object",
                                                                "required": [
                                                                    "name",
                                                                    "value"
                                                                ],
                                                                "properties": {
                                                                    "name": {
                                                                        "type": "string"
                                                                    },
                                                                    "value": {
                                                                        "type": "array",
                                                                        "items": {
                                                                            "anyOf": [
                                                                                {
                                                                                    "type": "string"
                                                                                },
                                                                                {
                                                                                    "type": "number"
                                                                                },
                                                                                {
                                                                                    "type": "integer"
                                                                                },
                                                                                {
                                                                                    "type": "array",
                                                                                    "items": {}
                                                                                },
                                                                                {
                                                                                    "type": "object"
                                                                                }
                                                                            ]
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                },
                                {
                                    "type": "object",
                                    "required": [
                                        "schema"
                                    ],
                                    "properties": {
                                        "schema": {
                                            "anyOf": [
                                                {
                                                    "type": "object",
                                                    "required": [
                                                        "$ref"
                                                    ],
                                                    "properties": {
                                                        "$ref": {
                                                            "type": "string",
                                                            "format": "uri-reference"
                                                        }
                                                    }
                                                },
                                                {
                                                    "type": "object",
                                                    "properties": {
                                                        "title": {
                                                            "type": "string"
                                                        },
                                                        "multipleOf": {
                                                            "type": "number",
                                                            "minimum": 0,
                                                            "exclusiveMinimum": True
                                                        },
                                                        "maximum": {
                                                            "type": "number"
                                                        },
                                                        "exclusiveMaximum": {
                                                            "type": "boolean",
                                                            "default": False
                                                        },
                                                        "minimum": {
                                                            "type": "number"
                                                        },
                                                        "exclusiveMinimum": {
                                                            "type": "boolean",
                                                            "default": False
                                                        },
                                                        "maxLength": {
                                                            "type": "integer",
                                                            "minimum": 0
                                                        },
                                                        "minLength": {
                                                            "type": "integer",
                                                            "minimum": 0,
                                                            "default": 0
                                                        },
                                                        "pattern": {
                                                            "type": "string",
                                                            "format": "regex"
                                                        },
                                                        "maxItems": {
                                                            "type": "integer",
                                                            "minimum": 0
                                                        },
                                                        "minItems": {
                                                            "type": "integer",
                                                            "minimum": 0,
                                                            "default": 0
                                                        },
                                                        "uniqueItems": {
                                                            "type": "boolean",
                                                            "default": False
                                                        },
                                                        "maxProperties": {
                                                            "type": "integer",
                                                            "minimum": 0
                                                        },
                                                        "minProperties": {
                                                            "type": "integer",
                                                            "minimum": 0,
                                                            "default": 0
                                                        },
                                                        "required": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "string"
                                                            },
                                                            "minItems": 1,
                                                            "uniqueItems": True
                                                        },
                                                        "enum": {
                                                            "type": "array",
                                                            "items": {},
                                                            "minItems": 1,
                                                            "uniqueItems": False
                                                        },
                                                        "type": {
                                                            "type": "string",
                                                            "enum": [
                                                                "array",
                                                                "boolean",
                                                                "integer",
                                                                "number",
                                                                "object",
                                                                "string"
                                                            ]
                                                        },
                                                        "not": {
                                                            "anyOf": [
                                                                {
                                                                    "type": "object",
                                                                    "required": [
                                                                        "$ref"
                                                                    ],
                                                                    "properties": {
                                                                        "$ref": {
                                                                            "type": "string",
                                                                            "format": "uri-reference"
                                                                        }
                                                                    }
                                                                }
                                                            ]
                                                        },
                                                        "allOf": {
                                                            "type": "array",
                                                            "items": {
                                                                "anyOf": [
                                                                    {
                                                                        "type": "object",
                                                                        "required": [
                                                                            "$ref"
                                                                        ],
                                                                        "properties": {
                                                                            "$ref": {
                                                                                "type": "string",
                                                                                "format": "uri-reference"
                                                                            }
                                                                        }
                                                                    }
                                                                ]
                                                            }
                                                        },
                                                        "anyOf": {
                                                            "type": "array",
                                                            "items": {
                                                                "anyOf": [
                                                                    {
                                                                        "type": "object",
                                                                        "required": [
                                                                            "$ref"
                                                                        ],
                                                                        "properties": {
                                                                            "$ref": {
                                                                                "type": "string",
                                                                                "format": "uri-reference"
                                                                            }
                                                                        }
                                                                    }
                                                                ]
                                                            }
                                                        },
                                                        "items": {
                                                            "anyOf": [
                                                                {
                                                                    "type": "object",
                                                                    "required": [
                                                                        "$ref"
                                                                    ],
                                                                    "properties": {
                                                                        "$ref": {
                                                                            "type": "string",
                                                                            "format": "uri-reference"
                                                                        }
                                                                    }
                                                                }
                                                            ]
                                                        },
                                                        "properties": {
                                                            "type": "object",
                                                            "additionalProperties": {
                                                                "anyOf": [
                                                                    {
                                                                        "type": "object",
                                                                        "required": [
                                                                            "$ref"
                                                                        ],
                                                                        "properties": {
                                                                            "$ref": {
                                                                                "type": "string",
                                                                                "format": "uri-reference"
                                                                            }
                                                                        }
                                                                    }
                                                                ]
                                                            }
                                                        },
                                                        "additionalProperties": {
                                                            "anyOf": [
                                                                {
                                                                    "type": "object",
                                                                    "required": [
                                                                        "$ref"
                                                                    ],
                                                                    "properties": {
                                                                        "$ref": {
                                                                            "type": "string",
                                                                            "format": "uri-reference"
                                                                        }
                                                                    }
                                                                },
                                                                {
                                                                    "type": "boolean"
                                                                }
                                                            ],
                                                            "default": True
                                                        },
                                                        "description": {
                                                            "type": "string"
                                                        },
                                                        "format": {
                                                            "type": "string"
                                                        },
                                                        "default": {},
                                                        "nullable": {
                                                            "type": "boolean",
                                                            "default": False
                                                        },
                                                        "readOnly": {
                                                            "type": "boolean",
                                                            "default": False
                                                        },
                                                        "writeOnly": {
                                                            "type": "boolean",
                                                            "default": False
                                                        },
                                                        "example": {},
                                                        "deprecated": {
                                                            "type": "boolean",
                                                            "default": False
                                                        },
                                                        "contentMediaType": {
                                                            "type": "string"
                                                        },
                                                        "contentEncoding": {
                                                            "type": "string"
                                                        },
                                                        "contentSchema": {
                                                            "type": "string"
                                                        }
                                                    },
                                                    "additionalProperties": False
                                                }
                                            ]
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        ]
    }
