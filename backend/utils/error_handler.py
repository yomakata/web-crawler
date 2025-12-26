"""
Error Handler Module
Provides user-friendly error messages and categorization for extraction failures
"""

import requests
from datetime import datetime
from typing import Dict, List, Optional, Any


class ExtractionError(Exception):
    """Base exception for extraction errors"""
    def __init__(self, message: str, error_type: str = "unknown_error", 
                 error_code: Optional[Any] = None, retry_possible: bool = False):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.error_code = error_code
        self.retry_possible = retry_possible


def get_http_error_suggestions(status_code: int) -> List[str]:
    """Get actionable suggestions based on HTTP status code"""
    suggestions = {
        400: [
            "Check if the URL is properly formatted",
            "Verify all required parameters are included",
            "Try accessing the URL directly in a browser"
        ],
        401: [
            "The page requires authentication",
            "Check if you have the necessary credentials",
            "This content may not be publicly accessible"
        ],
        403: [
            "Access to this resource is forbidden",
            "The website may be blocking automated access",
            "Try accessing the page in a browser to verify availability"
        ],
        404: [
            "Check if the URL is correct and complete",
            "Verify the page still exists on the website",
            "The page may have been moved or deleted"
        ],
        408: [
            "The request timed out",
            "Check your internet connection",
            "The server may be slow - try again later"
        ],
        429: [
            "Too many requests sent to the server",
            "Wait a few minutes before trying again",
            "The website may have rate limiting in place"
        ],
        500: [
            "The server encountered an internal error",
            "This is a server-side issue, not your fault",
            "Try again in a few minutes - the issue may be temporary"
        ],
        502: [
            "Bad gateway - the server received an invalid response",
            "This is a server infrastructure issue",
            "Wait a few minutes and try again"
        ],
        503: [
            "The service is temporarily unavailable",
            "The server may be down for maintenance",
            "Try again later when the service is restored"
        ],
        504: [
            "Gateway timeout - the server took too long to respond",
            "The website may be experiencing high traffic",
            "Try again in a few minutes"
        ]
    }
    
    # Default suggestions for unlisted codes
    default = [
        "An unexpected HTTP error occurred",
        "Try accessing the URL in a browser to verify it works",
        "Contact the website administrator if the problem persists"
    ]
    
    return suggestions.get(status_code, default)


def handle_extraction_failure(url: str, exception: Exception) -> Dict[str, Any]:
    """
    Map exceptions to user-friendly failure information
    
    Args:
        url: The URL that failed
        exception: The exception that was raised
        
    Returns:
        Dictionary with failure information
    """
    failure_info = {
        'extraction_status': 'failed',
        'url': url,
        'failure_reason': '',
        'error_type': '',
        'error_code': None,
        'error_timestamp': datetime.now().isoformat(),
        'retry_possible': False,
        'suggestions': []
    }
    
    # Handle different exception types
    if isinstance(exception, requests.Timeout):
        failure_info.update({
            'failure_reason': 'Connection timeout - Server took too long to respond',
            'error_type': 'network_error',
            'error_code': 'TIMEOUT',
            'retry_possible': True,
            'suggestions': [
                'Check your internet connection',
                'Try again in a few moments',
                'The target server may be slow or experiencing issues'
            ]
        })
        
    elif isinstance(exception, requests.ConnectionError):
        failure_info.update({
            'failure_reason': 'Connection refused - Unable to reach the server',
            'error_type': 'network_error',
            'error_code': 'CONNECTION_REFUSED',
            'retry_possible': True,
            'suggestions': [
                'Verify the URL is correct',
                'Check your internet connection',
                'The server may be down or unreachable',
                'Try again in a few minutes'
            ]
        })
        
    elif isinstance(exception, requests.HTTPError):
        status_code = exception.response.status_code
        reason = exception.response.reason
        failure_info.update({
            'failure_reason': f'{status_code} {reason}',
            'error_type': 'http_error',
            'error_code': status_code,
            'retry_possible': status_code >= 500,  # Server errors can be retried
            'suggestions': get_http_error_suggestions(status_code)
        })
        
    elif isinstance(exception, requests.TooManyRedirects):
        failure_info.update({
            'failure_reason': 'Too many redirects - The URL redirected too many times',
            'error_type': 'network_error',
            'error_code': 'TOO_MANY_REDIRECTS',
            'retry_possible': False,
            'suggestions': [
                'The URL may be misconfigured',
                'Try accessing the final destination URL directly',
                'Contact the website administrator'
            ]
        })
        
    elif isinstance(exception, ValueError):
        if 'Invalid URL' in str(exception):
            failure_info.update({
                'failure_reason': 'Invalid URL format - Please check the URL syntax',
                'error_type': 'validation_error',
                'error_code': 'INVALID_URL',
                'retry_possible': False,
                'suggestions': [
                    'Ensure the URL starts with http:// or https://',
                    'Check for typos in the URL',
                    'Verify the URL is complete and properly formatted'
                ]
            })
        elif 'Scoped element not found' in str(exception) or 'Element not found' in str(exception):
            error_msg = str(exception)
            
            # Check if authentication was successful based on error message
            auth_successful = '✓ Authentication successful' in error_msg
            
            if auth_successful:
                suggestions = [
                    '✓ Page was fetched successfully with authentication',
                    '✗ The specified CSS class or ID does not exist on this page',
                    'Verify the class name or ID is correct',
                    'Try extracting without scope restrictions to see full page content',
                    'Use Preview feature to inspect the actual page structure'
                ]
            else:
                suggestions = [
                    'Verify the class name or ID is correct',
                    'Check if the page structure has changed',
                    'If using authentication, verify credentials are correct',
                    'Try extracting without scope restrictions first',
                    'Inspect the page HTML to confirm the element exists'
                ]
            
            failure_info.update({
                'failure_reason': error_msg,
                'error_type': 'content_error',
                'error_code': 'ELEMENT_NOT_FOUND',
                'retry_possible': False,
                'suggestions': suggestions
            })
        else:
            failure_info.update({
                'failure_reason': f'Validation error - {str(exception)}',
                'error_type': 'validation_error',
                'error_code': 'VALIDATION_ERROR',
                'retry_possible': False,
                'suggestions': [
                    'Check the input parameters',
                    'Verify all required fields are provided correctly'
                ]
            })
            
    elif isinstance(exception, UnicodeDecodeError):
        failure_info.update({
            'failure_reason': 'Text encoding error - Unable to decode page content',
            'error_type': 'parsing_error',
            'error_code': 'ENCODING_ERROR',
            'retry_possible': True,
            'suggestions': [
                'The page may use an unsupported encoding',
                'Try again - encoding detection may succeed on retry',
                'Contact support if this error persists'
            ]
        })
        
    elif isinstance(exception, PermissionError):
        failure_info.update({
            'failure_reason': 'Permission denied - Unable to write output files',
            'error_type': 'permission_error',
            'error_code': 'PERMISSION_DENIED',
            'retry_possible': False,
            'suggestions': [
                'Check output directory permissions',
                'Ensure you have write access to the output folder',
                'Try specifying a different output directory'
            ]
        })
        
    elif isinstance(exception, OSError):
        if 'No space left on device' in str(exception):
            failure_info.update({
                'failure_reason': 'Disk space full - Unable to save extracted content',
                'error_type': 'permission_error',
                'error_code': 'DISK_FULL',
                'retry_possible': False,
                'suggestions': [
                    'Free up disk space on your device',
                    'Delete unnecessary files',
                    'Use a different output directory with more space'
                ]
            })
        else:
            failure_info.update({
                'failure_reason': f'File system error - {str(exception)}',
                'error_type': 'permission_error',
                'error_code': 'FILE_SYSTEM_ERROR',
                'retry_possible': False,
                'suggestions': [
                    'Check file system permissions',
                    'Verify the output path is accessible',
                    'Contact system administrator if needed'
                ]
            })
            
    elif 'Empty content' in str(exception) or 'No content' in str(exception):
        failure_info.update({
            'failure_reason': 'Empty content - No extractable content found on the page',
            'error_type': 'content_error',
            'error_code': 'EMPTY_CONTENT',
            'retry_possible': False,
            'suggestions': [
                'The page may be empty or contain only dynamic content',
                'Try a different URL',
                'Check if the page loads properly in a browser'
            ]
        })
        
    else:
        # Generic error handling
        error_message = str(exception)
        failure_info.update({
            'failure_reason': f'Extraction failed - {error_message}',
            'error_type': 'unknown_error',
            'error_code': 'UNKNOWN',
            'retry_possible': True,
            'suggestions': [
                'Try again in a few moments',
                'Check the URL is accessible in a browser',
                'Contact support if the problem persists'
            ]
        })
    
    return failure_info


def format_failure_for_api(failure_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format failure information for API response
    
    Args:
        failure_info: Raw failure information
        
    Returns:
        Formatted failure_info for API response
    """
    return {
        'failure_reason': failure_info['failure_reason'],
        'error_type': failure_info['error_type'],
        'error_code': failure_info['error_code'],
        'retry_possible': failure_info['retry_possible'],
        'suggestions': failure_info['suggestions']
    }


def create_failed_extraction_details(url: str, failure_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create extraction_details.json content for failed extractions
    
    Args:
        url: The URL that failed
        failure_info: Failure information from handle_extraction_failure
        
    Returns:
        Complete extraction details dictionary
    """
    return {
        'source_url': url,
        'timestamp': failure_info['error_timestamp'],
        'extraction_status': 'failed',
        'failure_reason': failure_info['failure_reason'],
        'error_type': failure_info['error_type'],
        'error_code': failure_info['error_code'],
        'retry_possible': failure_info['retry_possible'],
        'suggestions': failure_info['suggestions'],
        'execution_time': None,
        'http_response': None,
        'extraction_parameters': {},
        'content_statistics': None,
        'images': None,
        'output_files': [],
        'errors': [failure_info['failure_reason']],
        'warnings': []
    }
