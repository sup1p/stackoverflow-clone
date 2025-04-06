from copy import copy
from django.core.cache import cache
import json
import hashlib
from django.db.models import Q
from django.db.models import Count
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Post.models import Question, Answer, Vote, Tag
from Post.pagination import CustomPageNumberPagination, TagCustomPageNumberPagination
from Post.serializers import QuestionSerializer, AnswerSerializer
from Post.utils import add_reputation

@api_view(['GET', 'POST'])
def questions_list_and_create(request):
    query_params = request.query_params.dict()
    key_raw = json.dumps(query_params, sort_keys=True)
    key_hash = hashlib.md5(key_raw.encode()).hexdigest()
    cache_key = f"question_list:{key_hash}"

    cached_response = cache.get(cache_key)
    if cached_response:
        return Response(cached_response, status=status.HTTP_200_OK)

    if request.method == 'GET':
        queryset = Question.objects.all()

        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(content__icontains=search))

        tags = request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__name__in=tags).distinct()

        author = request.query_params.get('author')
        if author:
            queryset = queryset.filter(author__id=author)

        sort_by = request.query_params.get('sort_by')
        if sort_by:
            if sort_by == 'newest':
                queryset = queryset.order_by('-created_at')
            elif sort_by == 'active':
                queryset = queryset.order_by('-updated_at')
            elif sort_by == 'votes':
                queryset = queryset.order_by('-vote_count')
            elif sort_by == 'unanswered':
                queryset = queryset.filter(answer_count=0).order_by('-created_at')

        paginator = CustomPageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = QuestionSerializer(paginated_queryset, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)

        cache.set(cache_key, paginated_response.data, timeout=120)
        return paginated_response


    elif request.method == 'POST':

        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=401)

        serializer = QuestionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(author=request.user)

            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)



@api_view(['GET','PATCH','DELETE'])
def question_details_edit_delete(request, id):
    if request.method == 'GET':
        try:
            question = Question.objects.get(id=id)
        except Question.DoesNotExist:
            return Response({"message":"question not found by this id"},status=status.HTTP_404_NOT_FOUND)
        serializer = QuestionSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PATCH':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        """
        {
              "title": "string",
              "content": "string",
              "tags": ["string"]
        }
        """
        try:
            question = Question.objects.get(id=id)
        except Question.DoesNotExist:
            return Response({"message": "question not found by this id"}, status=status.HTTP_404_NOT_FOUND)


        if question.author != request.user:
            return Response({"message":"you are not the owner"}, status=status.HTTP_401_UNAUTHORIZED)
        new_title = request.data.get('title')
        new_content = request.data.get('content')
        new_tags = request.data.get('tags')

        if new_title and new_title != "" and new_title is not None:
            question.title = new_title
        if new_content and new_content != "" and new_content is not None:
            question.content = new_content
        if new_tags and new_tags != [] and new_tags is not None:
            question.tags = new_tags
        question.save()
        serializer = QuestionSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            question = Question.objects.get(id=id)
        except Question.DoesNotExist:
            return Response({"message": "question not found by this id"}, status=status.HTTP_404_NOT_FOUND)


        if question.author != request.user:
            return Response({"message":"you are not the owner"}, status=status.HTTP_401_UNAUTHORIZED)
        question.delete()
        return Response({"message":"question deleted"}, status=status.HTTP_204_NO_CONTENT)



@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def question_vote(request,id):
    """
    {
      "vote_type": "upvote" // или "downvote"
    }
    """
    try:
        question = Question.objects.get(id=id)
    except Question.DoesNotExist:
        return Response({"message":"question with this id does not exist"}, status=status.HTTP_404_NOT_FOUND)
    vote_type = request.data.get('vote_type')
    if vote_type not in ['upvote', 'downvote', 'Upvote', 'Downvote']:
        return Response({"message":"invalid vote_type"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        vote = Vote.objects.get(question=question,user=request.user)
        if vote.vote_type == vote_type:
            return Response({"message":"you have already cast this vote"}, status=status.HTTP_409_CONFLICT)
        else:
            old_vote = copy(vote.vote_type)
            vote.vote_type = vote_type
            vote.save()

            if old_vote == "upvote" and vote_type == "downvote":
                question.vote_count -= 2
                add_reputation(user_id=question.author_id, rep_type='question_downvote', change=-20,
                               description=f"Question was upvoted but now changed to downvoted:{question.title}")
            elif old_vote == "downvote" and vote_type == "upvote":
                question.vote_count += 2
                add_reputation(user_id=question.author_id, rep_type='question_downvote', change=20,
                               description=f"Question was downvated but now changed to upvoted:{question.title}")
            question.save()
    except Vote.DoesNotExist:
        Vote.objects.create(question=question, user=request.user, vote_type=vote_type)
        if vote_type == "upvote":
            question.vote_count += 1
            add_reputation(user_id=question.author_id,rep_type='question_upvote',change=10,
                            description=f"Question upvoted:{question.title}")
        elif vote_type == "downvote":
            question.vote_count -= 1
            add_reputation(user_id=question.author_id, rep_type='question_downvote', change=-10,
                            description=f"Question downvoted:{question.title}")
        question.save()
    serializer = QuestionSerializer(question)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET','POST'])
def answer_list_create(request):
    if request.method == 'GET':
        queryset = Answer.objects.all()
        question_id = request.query_params.get('question_id')
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({"message": "question with this id does not exist"}, status=status.HTTP_404_NOT_FOUND)
        queryset = queryset.filter(question_id=question_id)
        if request.query_params.get('author'):
            queryset = queryset.filter(author=request.query_params.get('author'))
        sort_by = request.query_params.get('sort_by')
        if sort_by:
            if sort_by == 'votes':
                queryset = queryset.order_by('-vote_count')
            elif sort_by == 'newest':
                queryset = queryset.order_by('-newest')
            elif sort_by == 'oldest':
                queryset = queryset.order_by('-oldest')

        paginator = CustomPageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = AnswerSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'},status=status.HTTP_401_UNAUTHORIZED)
        """
            {
            "question_id": "string",
            "content": "string"
            }
        """
        question_id = request.data.get('question_id')
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({"message": "question with this id does not exist"}, status=status.HTTP_404_NOT_FOUND)
        serializer = AnswerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, question=question)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','PATCH','DELETE'])
def answer_details_edit_delete(request,id):
    if request.method == 'GET':
        try:
            answer = Answer.objects.get(id=id)
        except Answer.DoesNotExist:
            return Response({"message": "answer with this id does not exist"}, status=status.HTTP_404_NOT_FOUND)
        serializer = AnswerSerializer(answer)
        return Response(serializer.data,status=status.HTTP_200_OK)
    elif request.method == 'PATCH':
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication credentials were not provided.'},status=status.HTTP_401_UNAUTHORIZED)
        try:
            answer = Answer.objects.get(id=id)
        except Answer.DoesNotExist:
            return Response({"message": "answer with this id does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if answer.author != request.user:
            return Response({'error':'you are not the owner'}, status=status.HTTP_403_FORBIDDEN)

        new_content = request.data.get('content')
        answer.content = new_content

        answer.save()

        serializer = AnswerSerializer(answer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication credentials were not provided.'},status=status.HTTP_401_UNAUTHORIZED)
        try:
            answer = Answer.objects.get(id=id)
        except Answer.DoesNotExist:
            return Response({"message": "answer with this id does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if answer.author != request.user:
            return Response({'error':'you are not the owner'}, status=status.HTTP_403_FORBIDDEN)
        answer.delete()
        return Response({"message": "answer deleted"}, status=status.HTTP_204_NO_CONTENT)



@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def answer_vote(request,id):
    """
        {
          "vote_type": "upvote" // или "downvote"
        }
        """
    try:
        answer = Answer.objects.get(id=id)
    except Answer.DoesNotExist:
        return Response({"message": "answer with this id does not exist"}, status=status.HTTP_404_NOT_FOUND)
    vote_type = request.data.get('vote_type')
    if vote_type not in ['upvote', 'downvote', 'Upvote', 'Downvote']:
        return Response({"message": "invalid vote_type"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        vote = Vote.objects.get(answer=answer, user=request.user)
        if vote.vote_type == vote_type:
            return Response({"message": "you have already cast this vote"}, status=status.HTTP_409_CONFLICT)
        else:
            old_vote = copy(vote.vote_type)
            vote.vote_type = vote_type
            vote.save()

            if old_vote == "upvote" and vote_type == "downvote":
                answer.vote_count -= 2
                add_reputation(user_id=answer.author_id, rep_type='answer_downvote', change=-40,
                               description=f"Answer was upvoted but now changed to downvoted ->:{answer.question.title}:{answer.content}")
            elif old_vote == "downvote" and vote_type == "upvote":
                answer.vote_count += 2
                add_reputation(user_id=answer.author_id, rep_type='answer_upvote', change=40,
                               description=f"Answer was downvoted but now changed to upvoted ->:{answer.question.title}:{answer.content}")
            answer.save()
    except Vote.DoesNotExist:
        Vote.objects.create(answer=answer, user=request.user, vote_type=vote_type)
        if vote_type == "upvote":
            answer.vote_count += 1
            add_reputation(user_id=answer.author_id, rep_type='answer_upvote', change=20,
                           description=f"Answer upvoted ->:{answer.question.title}:{answer.content}")
        elif vote_type == "downvote":
            answer.vote_count -= 1
            add_reputation(user_id=answer.author_id, rep_type='answer_downvote', change=-20,
                           description=f"Answer downvoted ->:{answer.question.title}:{answer.content}")
        answer.save()
    serializer = AnswerSerializer(answer)
    return Response(serializer.data, status=status.HTTP_200_OK)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def answer_accept(request, id):
    try:
        answer = Answer.objects.get(id=id)
        question = answer.question  # Получаем вопрос, к которому относится ответ

        # Проверка, что только автор вопроса может принимать ответ
        if request.user != question.author:
            return Response({'error': 'You are not the owner of this question'}, status=status.HTTP_403_FORBIDDEN)

        if answer.is_accepted:
            # Отклонение ответа
            answer.is_accepted = False
            answer.save()

            # Снижение репутации
            add_reputation(
                user_id=answer.author_id,
                rep_type='answer_accepted',
                change=-15,
                description=f"Answer was unaccepted for question: {question.title}"
            )
            serializer = AnswerSerializer(answer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        Answer.objects.filter(question=question, is_accepted=True).update(is_accepted=False)

        answer.is_accepted = True
        answer.save()

        add_reputation(
            user_id=answer.author_id,
            rep_type='answer_accepted',
            change=15,
            description=f"Answer accepted for question: {question.title}"
        )

        serializer = AnswerSerializer(answer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Answer.DoesNotExist:
        return Response({'error': 'Answer not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def tags_list(request):
    """
        Метод: GET
        Параметры запроса:
          - page: номер страницы (по умолчанию 1)
          - page_size: количество тегов на странице (по умолчанию 20)
          - search: поиск по имени тега
          - sort_by: 'popular', 'name', 'newest'
    """
    query_params = request.query_params.dict()
    key_raw = json.dumps(query_params, sort_keys=True)
    key_hash = hashlib.md5(key_raw.encode()).hexdigest()
    cache_key = f"tags_list:{key_hash}"

    cached_response = cache.get(cache_key)
    if cached_response:
        return Response(cached_response, status=status.HTTP_200_OK)

    queryset = Tag.objects.all()

    search = request.query_params.get('search')
    if search:
        queryset = queryset.filter(name__icontains=search)

    queryset = queryset.annotate(count=Count('questions'))

    sort_by = request.query_params.get('sort_by')
    if sort_by == 'name':
        queryset = queryset.order_by('name')
    elif sort_by == 'newest':
        queryset = queryset.order_by('-created_at')
    elif sort_by == 'popular':
        queryset = queryset.order_by('-count')

    paginator = TagCustomPageNumberPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)

    results = [
        {
            "id": tag.id,
            "name": tag.name,
            "description": tag.description,
            "count": tag.count
        }
        for tag in paginated_queryset
    ]
    paginated_response = paginator.get_paginated_response(results)
    cache.set(cache_key, paginated_response.data, timeout=120)
    return paginated_response


@api_view(['GET'])
def tags_details(request, id):
    try:
        tag = Tag.objects.get(id=id)
        count = tag.questions.count()
    except Tag.DoesNotExist:
        return Response({"message": "Tag not found"}, status=status.HTTP_404_NOT_FOUND)
    response_data = {
        "id": tag.id,
        "name": tag.name,
        "description": tag.description,
        "count": count  # Количество вопросов, использующих этот тег
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def tags_by_name(request,name):
    try:
        tag = Tag.objects.get(name=name)
        count = tag.questions.count()
    except Tag.DoesNotExist:
        return Response({"message": "Tag not found"}, status=status.HTTP_404_NOT_FOUND)
    response_data = {
        "id": tag.id,
        "name": tag.name,
        "description": tag.description,
        "count": count  # Количество вопросов, использующих этот тег
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def tags_search(request):
    """
    query parameters:
        `q`: string (required) - Search query
    """
    query = request.query_params.get('q')
    if not query:
        return Response({"message": "Search query 'q' is required"}, status=status.HTTP_400_BAD_REQUEST)

    tags = Tag.objects.filter(name__icontains=query)[:10]  #max 10 answers
    result = [{"id": tag.id, "name": tag.name} for tag in tags]
    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
def tag_questions(request,name):
    try:
        tag = Tag.objects.get(name=name)
    except Tag.DoesNotExist:
        return Response({"message": "Tag not found"}, status=status.HTTP_404_NOT_FOUND)

    queryset = Question.objects.filter(tags=tag)

    sort_by = request.query_params.get('sort_by')
    if sort_by == 'votes':
        queryset = queryset.order_by('-vote_count')
    elif sort_by == 'active':
        queryset = queryset.order_by('-updated_at')
    elif sort_by == 'newest':
        queryset = queryset.order_by('-created_at')

    paginator = CustomPageNumberPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = QuestionSerializer(paginated_queryset, many=True)

    return paginator.get_paginated_response(serializer.data)