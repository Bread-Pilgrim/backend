class ErrorCode:
    # 알 수 없는 오류
    UNKNOWN_ERROR = 1000
    # 토큰 만료 오류
    UNAUTHORIZED = 1001
    # 요청 누락
    REQUEST_MISSING = 1002
    # not found
    NOT_FOUND_DATA = 1004
    # 정렬데이터 올바르게 안보냈을 때,
    INVALID_SORT_PARAM = 1005
    # 잘못된 지역코드
    INVALID_AREA_CODE = 1006
    # 잘못된 파일 형식일 때,
    INVALID_FILE_CONTENT_TYPE = 1007
    # 이미지 파일 변환 실패
    CONVERT_IMAGE_EXT = 1008
    # 중복데이터
    DUPLICATE_DATA = 1009
    # 파입업로드 실패
    FAIL_UPLOAD_FILE = 1010
    # 리뷰 작성 개수 초과
    REVIEW_LIMIT_EXCEED = 1011
