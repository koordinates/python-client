#Get multiple tokens response
token_get_multiple_tokens_good_response = '''[{"name": "", "key_hint": "0fooxx...", "url": "https://test.koordinates.com/services/api/v1/tokens/987654/"}]'''
#Get single tokens response
token_get_single_token_good_response = '''{"name": "", "key_hint": "0fooxx...", "url": "https://test.koordinates.com/services/api/v1/tokens/987654/", "created_at": "2015-06-29T05:11:35.769Z", "expires_at": null, "scope": "query tiles catalog wxs:wfs wxs:wms wxs:wcs documents:read documents:write layers:read layers:write sets:read sets:write sources:read sources:write users:read users:write tokens:read tokens:write", "referrers": null}'''
#Create Token response
token_good_create = '''{"name": "Sample Token for Testing", "key_hint": "7fooxx...", "url": "https://test.koordinates.com/services/api/v1/tokens/987659/", "created_at": "2015-07-06T01:17:07.120Z", "expires_at": "2015-08-01T08:00:00Z", "scope": "query tiles catalog wxs:wfs wxs:wms wxs:wcs", "referrers": [], "key": "77777777777777777777777777777777"}'''
